"""PostgreSQL utilities."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_postgres_engine(database_url: str):
    """Create PostgreSQL async engine."""
    return create_async_engine(
        database_url,
        echo=False,
        pool_size=20,
        max_overflow=0,
    )


def get_postgres_session(engine) -> async_sessionmaker:
    """Create PostgreSQL async session maker."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db_session(session_maker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
