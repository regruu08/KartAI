"""Async SQLAlchemy 2.0 Database Engine and Session Management.

Provides asynchronous database engine, session factory, connection lifecycle hooks,
and FastAPI dependency injection for ReturnZero AI per ADR-019.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.config import get_settings, resolve_database_url
from app.db.models import Base

settings = get_settings()


def create_session_engine(database_url: str) -> AsyncEngine:
    """Create a configured AsyncEngine for SQLite or PostgreSQL."""
    resolved_url = resolve_database_url(database_url)
    engine_kwargs: dict[str, Any] = {
        "echo": False,
        "future": True,
    }

    if ":memory:" in resolved_url:
        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    eng: AsyncEngine = create_async_engine(resolved_url, **engine_kwargs)

    @event.listens_for(eng.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        """Enforce foreign key integrity and WAL mode on SQLite connections."""
        if not resolved_url.startswith("sqlite"):
            return
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        finally:
            cursor.close()

    return eng


def create_session_factory(target_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a configured async session factory bound to the supplied engine."""
    return async_sessionmaker(
        bind=target_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# Primary async engine and session factory
engine: AsyncEngine = create_session_engine(settings.DATABASE_URL)
async_session_factory = create_session_factory(engine)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an isolated asynchronous database session."""
    factory: async_sessionmaker[AsyncSession] = getattr(
        request.app.state, "session_factory", async_session_factory
    )
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(engine_override: AsyncEngine | None = None) -> None:
    """Create all relational tables defined in the declarative schema."""
    target_engine = engine_override or engine
    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_db(engine_override: AsyncEngine | None = None) -> None:
    """Drop and recreate all tables for a pristine demo environment."""
    target_engine = engine_override or engine
    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
