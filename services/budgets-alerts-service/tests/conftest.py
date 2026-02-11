"""
Pytest configuration and fixtures for budgets-alerts-service tests.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import AsyncGenerator

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from models.models import Base, Budget, BudgetPeriod, BudgetStatus


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def sample_budget_data():
    """Sample budget data for testing."""
    now = datetime.utcnow()
    return {
        "org_id": "org-123",
        "tenant_id": "tenant-456",
        "name": "Production Budget",
        "description": "Monthly production environment budget",
        "amount": 10000.0,
        "period": BudgetPeriod.MONTHLY,
        "start_date": now,
        "end_date": now + timedelta(days=30),
        "filters": {"cloud_provider": "aws", "environment": "production"},
        "thresholds": [50, 80, 90, 100],
    }


@pytest.fixture
def synthetic_cost_data():
    """Generate synthetic cost data for testing."""
    def _generate(days: int = 30, daily_avg: float = 300.0, variance: float = 0.2):
        """Generate synthetic daily cost data."""
        import random
        cost_data = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(days):
            # Add variance and slight upward trend
            variance_factor = random.uniform(1 - variance, 1 + variance)
            trend_factor = 1 + (i * 0.01)  # 1% daily increase
            daily_cost = daily_avg * variance_factor * trend_factor
            
            cost_data.append({
                "date": base_date + timedelta(days=i),
                "amount": daily_cost,
            })
        
        return cost_data
    
    return _generate
