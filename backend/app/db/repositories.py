"""Asynchronous Database Repository Layer for ReturnZero AI.

Provides typed repository interfaces for SKUs, Orders, Fit Logs, Incentive Interventions,
Delivery Events, and live SQL-aggregated Merchant Analytics per ADR-005, ADR-006, and ADR-019.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    DeliveryEventModel,
    FitLogModel,
    IncentiveInterventionModel,
    OrderModel,
    SkuModel,
)
from app.schemas.api_contracts import (
    AnalyticsOverviewResponse,
    OrderOutcomeStatus,
    SkuMetricStat,
    TierRtoStat,
)

# Canonical RTO and Customer Return status sets
RTO_STATUSES: tuple[str, ...] = (
    OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
    OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
    OrderOutcomeStatus.PREPAID_RTO_RELOCATED.value,
)

CUSTOMER_RETURN_STATUSES: tuple[str, ...] = (
    OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
    OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
)

ACTIVE_ORDER_STATUSES: tuple[str, ...] = (
    OrderOutcomeStatus.PLACED.value,
    OrderOutcomeStatus.SAFE_FOR_DISPATCH.value,
    OrderOutcomeStatus.ADDRESS_UPDATED.value,
    OrderOutcomeStatus.DELIVERY_RESCHEDULED.value,
    OrderOutcomeStatus.NDR.value,
    OrderOutcomeStatus.NDR_RESOLVED.value,
)


class SkuRepository:
    """Asynchronous repository for product SKU entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, sku_id: str) -> SkuModel | None:
        """Retrieve SKU by unique primary key."""
        stmt = select(SkuModel).where(SkuModel.id == sku_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[SkuModel]:
        """List all available product catalog SKUs."""
        stmt = select(SkuModel).order_by(SkuModel.id.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, sku: SkuModel) -> SkuModel:
        """Persist a new SKU record."""
        self.session.add(sku)
        await self.session.flush()
        return sku

    async def upsert(self, sku: SkuModel) -> SkuModel:
        """Insert or update an SKU entity."""
        existing = await self.get_by_id(sku.id)
        if existing:
            existing.name = sku.name
            existing.category = sku.category
            existing.price_inr = sku.price_inr
            existing.fabric_composition = sku.fabric_composition
            existing.fabric_stretch = sku.fabric_stretch
            existing.has_shoulder = sku.has_shoulder
            existing.has_sleeve = sku.has_sleeve
            existing.length_inches = sku.length_inches
            existing.sizes_json = sku.sizes_json
            existing.care_instructions = sku.care_instructions
            existing.provenance = sku.provenance
            existing.extracted_at = sku.extracted_at
            existing.prompt_version = sku.prompt_version
            existing.image_sha256 = sku.image_sha256
            await self.session.flush()
            return existing
        self.session.add(sku)
        await self.session.flush()
        return sku


class OrderRepository:
    """Asynchronous repository for Customer Order entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, order_id: str) -> OrderModel | None:
        """Retrieve order by internal primary key."""
        stmt = (
            select(OrderModel)
            .options(
                selectinload(OrderModel.interventions),
                selectinload(OrderModel.delivery_events),
                selectinload(OrderModel.fit_logs),
            )
            .where(OrderModel.id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str) -> OrderModel | None:
        """Retrieve order by merchant order number."""
        stmt = select(OrderModel).where(OrderModel.order_number == order_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_orders(self, limit: int = 150, offset: int = 0) -> Sequence[OrderModel]:
        """List orders ordered by creation date descending."""
        stmt = select(OrderModel).order_by(OrderModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_orders(self) -> int:
        """Count total orders in persistence."""
        stmt = select(func.count()).select_from(OrderModel)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, order: OrderModel) -> OrderModel:
        """Persist a new order record."""
        self.session.add(order)
        await self.session.flush()
        return order

    async def update_status(
        self,
        order_id: str,
        status: str,
        address_status: str | None = None,
    ) -> OrderModel | None:
        """Update order lifecycle status and optional address status."""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        order.order_status = status
        if address_status is not None:
            order.address_status = address_status
        await self.session.flush()
        return order


class FitLogRepository:
    """Asynchronous repository for sizing consultation logs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, fit_log: FitLogModel) -> FitLogModel:
        """Persist a new sizing recommendation log."""
        self.session.add(fit_log)
        await self.session.flush()
        return fit_log

    async def get_by_id(self, log_id: str) -> FitLogModel | None:
        """Retrieve sizing consultation log by ID."""
        stmt = select(FitLogModel).where(FitLogModel.id == log_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_sku(self, sku_id: str) -> Sequence[FitLogModel]:
        """List sizing consultation logs for a given SKU."""
        stmt = (
            select(FitLogModel)
            .where(FitLogModel.sku_id == sku_id)
            .order_by(FitLogModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class IncentiveRepository:
    """Asynchronous repository for UPI conversion incentive interventions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, intervention: IncentiveInterventionModel) -> IncentiveInterventionModel:
        """Persist an incentive quote and conversion record."""
        self.session.add(intervention)
        await self.session.flush()
        return intervention

    async def get_by_order_id(self, order_id: str) -> Sequence[IncentiveInterventionModel]:
        """Retrieve interventions associated with an order."""
        stmt = (
            select(IncentiveInterventionModel)
            .where(IncentiveInterventionModel.order_id == order_id)
            .order_by(IncentiveInterventionModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class DeliveryEventRepository:
    """Asynchronous repository for delivery assurance events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: DeliveryEventModel) -> DeliveryEventModel:
        """Persist a new delivery event."""
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_by_order_id(self, order_id: str) -> Sequence[DeliveryEventModel]:
        """Retrieve chronological delivery events for an order."""
        stmt = (
            select(DeliveryEventModel)
            .where(DeliveryEventModel.order_id == order_id)
            .order_by(DeliveryEventModel.timestamp.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class AnalyticsRepository:
    """SQL Aggregations for Live Merchant Intelligence Dashboard.

    Strictly queries real database rows to produce dynamic telemetry without
    mixing in hypothetical scenario projections (ADR-005, E5).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_live_overview(self) -> AnalyticsOverviewResponse:
        """Aggregate dynamic KPIs directly from database tables."""
        # 1. Total order counts and status breakdowns
        order_metrics_stmt = select(
            func.count(OrderModel.id).label("total_orders"),
            func.sum(case((OrderModel.payment_method == "COD", 1), else_=0)).label("cod_orders"),
            func.sum(case((OrderModel.payment_method == "Prepaid", 1), else_=0)).label(
                "prepaid_orders"
            ),
            func.sum(case((OrderModel.order_status.in_(RTO_STATUSES), 1), else_=0)).label(
                "rto_orders"
            ),
            func.sum(
                case((OrderModel.order_status.in_(CUSTOMER_RETURN_STATUSES), 1), else_=0)
            ).label("return_orders"),
            func.sum(
                case(
                    (OrderModel.order_status == OrderOutcomeStatus.DELIVERED_KEPT.value, 1), else_=0
                )
            ).label("delivered_kept_orders"),
            func.sum(case((OrderModel.order_status.in_(ACTIVE_ORDER_STATUSES), 1), else_=0)).label(
                "active_orders"
            ),
        )
        order_res = await self.session.execute(order_metrics_stmt)
        row = order_res.one()

        total_orders = int(row.total_orders or 0)
        cod_orders = int(row.cod_orders or 0)
        prepaid_orders = int(row.prepaid_orders or 0)
        rto_count = int(row.rto_orders or 0)
        customer_returns = int(row.return_orders or 0)
        delivered_kept = int(row.delivered_kept_orders or 0)
        active_orders = int(row.active_orders or 0)

        cod_share_pct = round((cod_orders / total_orders * 100.0), 2) if total_orders > 0 else 0.0
        rto_rate_pct = round((rto_count / total_orders * 100.0), 2) if total_orders > 0 else 0.0
        customer_return_rate_pct = (
            round((customer_returns / total_orders * 100.0), 2) if total_orders > 0 else 0.0
        )
        delivered_kept_rate_pct = (
            round((delivered_kept / total_orders * 100.0), 2) if total_orders > 0 else 0.0
        )

        # 2. Incentive intervention aggregations
        incentive_metrics_stmt = select(
            func.count(IncentiveInterventionModel.id).label("total_interventions"),
            func.sum(
                case((IncentiveInterventionModel.converted_to_upi.is_(True), 1), else_=0)
            ).label("converted_orders"),
            func.sum(
                case(
                    (
                        IncentiveInterventionModel.converted_to_upi.is_(True),
                        IncentiveInterventionModel.expected_savings_inr,
                    ),
                    else_=Decimal("0.00"),
                )
            ).label("total_savings"),
            func.sum(
                case(
                    (
                        IncentiveInterventionModel.converted_to_upi.is_(True),
                        IncentiveInterventionModel.offered_discount_inr,
                    ),
                    else_=Decimal("0.00"),
                )
            ).label("total_discounts"),
        )
        incentive_res = await self.session.execute(incentive_metrics_stmt)
        inc_row = incentive_res.one()

        converted_to_upi = int(inc_row.converted_orders or 0)
        estimated_direct_savings = Decimal(str(inc_row.total_savings or "0.00"))
        total_disbursed = Decimal(str(inc_row.total_discounts or "0.00"))

        # 3. Tier RTO breakdown
        tier_breakdown_stmt = (
            select(
                OrderModel.tier,
                func.count(OrderModel.id).label("tier_orders"),
                func.sum(case((OrderModel.order_status.in_(RTO_STATUSES), 1), else_=0)).label(
                    "tier_rto"
                ),
            )
            .group_by(OrderModel.tier)
            .order_by(OrderModel.tier.asc())
        )
        tier_res = await self.session.execute(tier_breakdown_stmt)
        tier_stats: list[TierRtoStat] = []
        for t_row in tier_res.all():
            t_orders = int(t_row.tier_orders or 0)
            t_rto = int(t_row.tier_rto or 0)
            t_rate = round((t_rto / t_orders * 100.0), 2) if t_orders > 0 else 0.0
            tier_stats.append(
                TierRtoStat(
                    tier=str(t_row.tier),
                    total_orders=t_orders,
                    rto_count=t_rto,
                    rto_rate_pct=t_rate,
                )
            )

        # 4. SKU intelligence breakdown
        sku_stmt = select(SkuModel).order_by(SkuModel.id.asc())
        sku_res = await self.session.execute(sku_stmt)
        all_skus = sku_res.scalars().all()

        sku_metrics_stmt = select(
            OrderModel.sku_id,
            func.count(OrderModel.id).label("sku_orders"),
            func.sum(case((OrderModel.order_status.in_(RTO_STATUSES), 1), else_=0)).label(
                "sku_rto"
            ),
            func.sum(
                case(
                    (OrderModel.order_status == OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value, 1),
                    else_=0,
                )
            ).label("sku_fit_returns"),
            func.sum(
                case(
                    (
                        OrderModel.order_status
                        == OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
                        1,
                    ),
                    else_=0,
                )
            ).label("sku_defect_returns"),
            func.sum(case((OrderModel.used_fit_check.is_(False), 1), else_=0)).label(
                "sku_no_fit_check"
            ),
        ).group_by(OrderModel.sku_id)
        sku_metrics_res = await self.session.execute(sku_metrics_stmt)
        sku_metrics_map = {row.sku_id: row for row in sku_metrics_res.all()}

        sku_stats: list[SkuMetricStat] = []
        for sku in all_skus:
            s_row = sku_metrics_map.get(sku.id)
            s_orders = int(s_row.sku_orders or 0) if s_row else 0
            s_rto = int(s_row.sku_rto or 0) if s_row else 0
            s_fit = int(s_row.sku_fit_returns or 0) if s_row else 0
            s_defect = int(s_row.sku_defect_returns or 0) if s_row else 0
            s_bracketing = int(s_row.sku_no_fit_check or 0) if s_row else 0

            s_rto_rate = round((s_rto / s_orders * 100.0), 2) if s_orders > 0 else 0.0
            s_fit_rate = round((s_fit / s_orders * 100.0), 2) if s_orders > 0 else 0.0
            s_defect_rate = round((s_defect / s_orders * 100.0), 2) if s_orders > 0 else 0.0

            has_missing = not (sku.has_sleeve and sku.has_shoulder)
            alert = None
            if not sku.has_sleeve:
                alert = "Add sleeve length to improve fit confidence"

            sku_stats.append(
                SkuMetricStat(
                    sku_id=sku.id,
                    sku_name=sku.name,
                    total_orders=s_orders,
                    rto_count=s_rto,
                    rto_rate_pct=s_rto_rate,
                    fit_return_count=s_fit,
                    fit_return_rate_pct=s_fit_rate,
                    defect_return_count=s_defect,
                    defect_return_rate_pct=s_defect_rate,
                    bracketing_count=s_bracketing,
                    has_missing_measurements=has_missing,
                    alert_message=alert,
                )
            )

        return AnalyticsOverviewResponse(
            total_orders=total_orders,
            cod_orders_count=cod_orders,
            prepaid_orders_count=prepaid_orders,
            cod_share_pct=cod_share_pct,
            rto_count=rto_count,
            rto_rate_pct=rto_rate_pct,
            customer_return_count=customer_returns,
            customer_return_rate_pct=customer_return_rate_pct,
            delivered_kept_count=delivered_kept,
            delivered_kept_rate_pct=delivered_kept_rate_pct,
            active_orders_count=active_orders,
            converted_to_upi_count=converted_to_upi,
            estimated_direct_savings_inr=estimated_direct_savings,
            total_incentives_disbursed_inr=total_disbursed,
            tier_breakdown=tier_stats,
            sku_breakdown=sku_stats,
            disclaimer=(
                "modelled direct operating savings after incentives, before fees — "
                "excluding tax, overhead, and other non-delivery costs."
            ),
        )
