"""SQLAlchemy 2.0 Declarative Async Models for ReturnZero AI.

Defines persistence models for SKUs, Orders, Fit Logs, Incentive Interventions,
and Delivery Events per ADR-005, ADR-006, ADR-009, and ADR-019.
All models use DeclarativeBase, Mapped, and mapped_column with PostgreSQL compatibility.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Common declarative base class for all ReturnZero AI entities."""

    type_annotation_map = {
        dict[str, Any]: JSON().with_variant(SQLITE_JSON, "sqlite"),
        list[Any]: JSON().with_variant(SQLITE_JSON, "sqlite"),
    }


class SkuModel(Base):
    """Product catalog SKU entity representing fashion apparel items."""

    __tablename__ = "skus"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    price_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fabric_composition: Mapped[str] = mapped_column(String(255), nullable=False)
    fabric_stretch: Mapped[str] = mapped_column(String(50), nullable=False)
    has_shoulder: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_sleeve: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    length_inches: Mapped[float | None] = mapped_column(Float, nullable=True)
    sizes_json: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(SQLITE_JSON, "sqlite"),
        nullable=False,
        default=dict,
    )
    care_instructions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provenance: Mapped[str] = mapped_column(String(50), default="manual_fixture", nullable=False)
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    image_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    orders: Mapped[list[OrderModel]] = relationship(
        back_populates="sku",
        cascade="all, delete-orphan",
    )
    fit_logs: Mapped[list[FitLogModel]] = relationship(
        back_populates="sku",
        cascade="all, delete-orphan",
    )


class OrderModel(Base):
    """Customer order entity tracking financial, sizing, risk, and delivery assurance lifecycle."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    street_address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pin_code: Mapped[str] = mapped_column(String(10), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False)  # "Tier-1", "Tier-2", "Tier-3"
    address_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Complete")
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False, default="COD")
    order_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Placed")
    total_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cod_risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    discount_applied_inr: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    selected_size: Mapped[str] = mapped_column(String(20), nullable=False)
    sku_id: Mapped[str] = mapped_column(String(50), ForeignKey("skus.id"), nullable=False)
    used_fit_check: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    consent_status: Mapped[str] = mapped_column(String(50), default="opted_in", nullable=False)
    dispatch_priority: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Composite indexes for query acceleration
    __table_args__ = (
        Index("ix_orders_synthetic_payment", "is_synthetic", "payment_method"),
        Index("ix_orders_tier_status", "tier", "order_status"),
        Index("ix_orders_created_at", "created_at"),
        Index("ix_orders_sku_id", "sku_id"),
    )

    # Relationships
    sku: Mapped[SkuModel] = relationship(back_populates="orders")
    interventions: Mapped[list[IncentiveInterventionModel]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    delivery_events: Mapped[list[DeliveryEventModel]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    fit_logs: Mapped[list[FitLogModel]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class FitLogModel(Base):
    """Fit-Twin sizing consultation audit log."""

    __tablename__ = "fit_logs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(50), ForeignKey("skus.id"), nullable=False)
    order_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("orders.id"), nullable=True)
    known_brand: Mapped[str] = mapped_column(String(100), nullable=False)
    known_size: Mapped[str] = mapped_column(String(20), nullable=False)
    recommended_size: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(50), nullable=False)
    fit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    sku: Mapped[SkuModel] = relationship(back_populates="fit_logs")
    order: Mapped[OrderModel | None] = relationship(back_populates="fit_logs")


class IncentiveInterventionModel(Base):
    """Incentive optimizer quotation and conversion tracking entity."""

    __tablename__ = "incentive_interventions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(50), ForeignKey("orders.id"), nullable=False)
    original_payment: Mapped[str] = mapped_column(String(20), nullable=False, default="COD")
    offered_discount_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    converted_to_upi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expected_savings_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    retained_headroom_inr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    order: Mapped[OrderModel] = relationship(back_populates="interventions")


class DeliveryEventModel(Base):
    """Chronological courier and delivery assurance event log for an order."""

    __tablename__ = "delivery_events"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(50), ForeignKey("orders.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    clarified_landmark: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    order: Mapped[OrderModel] = relationship(back_populates="delivery_events")
