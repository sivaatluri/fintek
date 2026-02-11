"""
Tests for budget threshold detector.
"""

import pytest
from datetime import datetime, timedelta
import uuid

from models.models import Budget, BudgetPeriod
from detectors.threshold_detector import BudgetThresholdDetector


@pytest.mark.asyncio
async def test_threshold_50_percent(db_session, sample_budget_data, synthetic_cost_data):
    """Test 50% threshold detection."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget_data["thresholds"] = [50, 80, 90, 100]
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate cost data at 55% of budget
    target_spend = budget.amount * 0.55
    cost_data = synthetic_cost_data(days=15, daily_avg=target_spend / 15)
    
    # Run detector
    detector = BudgetThresholdDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should detect 50% threshold
    assert result is not None
    assert result.detected is True
    assert result.details["threshold_percentage"] == 50
    assert result.severity in ["low", "medium"]


@pytest.mark.asyncio
async def test_threshold_90_percent(db_session, sample_budget_data, synthetic_cost_data):
    """Test 90% threshold detection."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate cost data at 95% of budget
    target_spend = budget.amount * 0.95
    cost_data = synthetic_cost_data(days=28, daily_avg=target_spend / 28)
    
    # Run detector
    detector = BudgetThresholdDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should detect 90% threshold
    assert result is not None
    assert result.detected is True
    assert result.details["threshold_percentage"] == 90
    assert result.severity == "high"


@pytest.mark.asyncio
async def test_threshold_100_percent(db_session, sample_budget_data, synthetic_cost_data):
    """Test 100% threshold detection."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate cost data at 105% of budget
    target_spend = budget.amount * 1.05
    cost_data = synthetic_cost_data(days=30, daily_avg=target_spend / 30)
    
    # Run detector
    detector = BudgetThresholdDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should detect 100% threshold
    assert result is not None
    assert result.detected is True
    assert result.details["threshold_percentage"] == 100
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_no_threshold_exceeded(db_session, sample_budget_data, synthetic_cost_data):
    """Test when no threshold is exceeded."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate cost data at 30% of budget
    target_spend = budget.amount * 0.30
    cost_data = synthetic_cost_data(days=10, daily_avg=target_spend / 10)
    
    # Run detector
    detector = BudgetThresholdDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should not detect
    assert result is None


@pytest.mark.asyncio
async def test_threshold_state_tracking(db_session, sample_budget_data, synthetic_cost_data):
    """Test that threshold state prevents duplicate alerts."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget_data["alert_state"] = {"threshold_50": True}  # Already alerted at 50%
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate cost data at 55% (should not alert again for 50%)
    target_spend = budget.amount * 0.55
    cost_data = synthetic_cost_data(days=15, daily_avg=target_spend / 15)
    
    # Run detector
    detector = BudgetThresholdDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should not detect (already alerted)
    assert result is None
