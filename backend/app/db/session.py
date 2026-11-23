"""Async SQLAlchemy 2.0 Database Engine and Session Management.

Provides asynchronous database engine, session factory, connection lifecycle hooks,
and FastAPI dependency injection for ReturnZero AI per ADR-019.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.db.models import Base

settings = get_settings()


def create_session_engine(database_url: str) -> AsyncEngine:
    """Create a configured AsyncEngine for SQLite or PostgreSQL."""
    engine_kwargs: dict[str, Any] = {
        "echo": False,
        "future": True,
    }

    if ":memory:" in database_url:
        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    eng: AsyncEngine = create_async_engine(database_url, **engine_kwargs)

    @event.listens_for(eng.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        """Enforce foreign key integrity and WAL mode on SQLite connections."""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        finally:
            cursor.close()

    return eng


# Primary async engine and session factory
engine: AsyncEngine = create_session_engine(settings.DATABASE_URL)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an isolated asynchronous database session."""
    async with async_session_factory() as session:
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
