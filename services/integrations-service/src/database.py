"""Database connection management."""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from finops_common import get_logger

logger = get_logger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://finops:finops@localhost:5432/finops"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database connection."""
    logger.info(f"Initializing database connection to {DATABASE_URL}")
    # Test connection
    async with engine.begin() as conn:
        await conn.execute("SELECT 1")
    logger.info("Database connection established")


async def close_db() -> None:
    """Close database connection."""
    logger.info("Closing database connection")
    await engine.dispose()
