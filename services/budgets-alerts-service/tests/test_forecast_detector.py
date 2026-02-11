"""
Tests for forecast detector.
"""

import pytest
from datetime import datetime, timedelta
import uuid

from models.models import Budget, BudgetPeriod
from detectors.forecast_detector import ForecastDetector


@pytest.mark.asyncio
async def test_forecast_exceeds_budget(db_session, sample_budget_data):
    """Test forecast detection when trend exceeds budget."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget_data["amount"] = 10000.0
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate upward trending cost data
    cost_data = []
    base_date = budget.start_date
    
    for i in range(15):  # 15 days of data
        # Strong upward trend that will exceed budget
        daily_cost = 400 + (i * 50)  # Increasing daily cost
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": daily_cost,
        })
    
    # Run detector
    detector = ForecastDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should detect forecast exceeding budget
    assert result is not None
    assert result.detected is True
    assert result.details["forecast_amount"] > budget.amount
    assert "confidence" in result.details


@pytest.mark.asyncio
async def test_forecast_within_budget(db_session, sample_budget_data):
    """Test when forecast stays within budget."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget_data["amount"] = 10000.0
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate flat cost data
    cost_data = []
    base_date = budget.start_date
    
    for i in range(15):
        # Flat daily cost that won't exceed budget
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": 200.0,  # $200/day = $6000/month
        })
    
    # Run detector
    detector = ForecastDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should not detect
    assert result is None


@pytest.mark.asyncio
async def test_forecast_insufficient_data(db_session, sample_budget_data):
    """Test with insufficient data (< 7 days)."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate only 5 days of data
    cost_data = []
    base_date = budget.start_date
    
    for i in range(5):
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": 500.0,
        })
    
    # Run detector
    detector = ForecastDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should not detect (insufficient data)
    assert result is None
