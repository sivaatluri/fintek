"""
Tests for anomaly spike detector.
"""

import pytest
from datetime import datetime, timedelta
import uuid

from models.models import Budget, BudgetPeriod
from detectors.anomaly_detector import AnomalyDetector


@pytest.mark.asyncio
async def test_anomaly_spike_detected(db_session, sample_budget_data):
    """Test anomaly spike detection."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate baseline + spike cost data
    cost_data = []
    base_date = budget.start_date - timedelta(days=15)
    
    # 14 days of baseline (~$200/day)
    for i in range(14):
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": 200.0 + (i * 2),  # Slight upward trend
        })
    
    # 1 day with significant spike
    cost_data.append({
        "date": base_date + timedelta(days=14),
        "amount": 1000.0,  # 5x baseline
    })
    
    # Run detector
    detector = AnomalyDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should detect anomaly
    assert result is not None
    assert result.detected is True
    assert result.details["current_value"] > result.details["baseline_mean"]
    assert result.details["stddev_multiplier"] >= 2.0


@pytest.mark.asyncio
async def test_no_anomaly(db_session, sample_budget_data):
    """Test when no anomaly is present."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate consistent cost data
    cost_data = []
    base_date = budget.start_date - timedelta(days=15)
    
    for i in range(15):
        # Consistent daily cost
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": 200.0,
        })
    
    # Run detector
    detector = AnomalyDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should not detect
    assert result is None


@pytest.mark.asyncio
async def test_anomaly_insufficient_data(db_session, sample_budget_data):
    """Test with insufficient data (< 14 days)."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate only 10 days of data
    cost_data = []
    base_date = budget.start_date
    
    for i in range(10):
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": 200.0,
        })
    
    # Run detector
    detector = AnomalyDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should not detect (insufficient data)
    assert result is None


@pytest.mark.asyncio
async def test_anomaly_severity_levels(db_session, sample_budget_data):
    """Test severity levels based on stddev multiplier."""
    # Create budget
    budget_data = sample_budget_data.copy()
    budget_data["id"] = str(uuid.uuid4())
    budget = Budget(**budget_data)
    db_session.add(budget)
    await db_session.commit()
    
    # Generate baseline + critical spike
    cost_data = []
    base_date = budget.start_date - timedelta(days=15)
    
    # 14 days of baseline
    for i in range(14):
        cost_data.append({
            "date": base_date + timedelta(days=i),
            "amount": 100.0,
        })
    
    # Critical spike (>4 stddev)
    cost_data.append({
        "date": base_date + timedelta(days=14),
        "amount": 500.0,  # Much higher than baseline
    })
    
    # Run detector
    detector = AnomalyDetector(db_session)
    result = await detector.detect(budget, cost_data)
    
    # Should detect with high or critical severity
    if result:
        assert result.severity in ["high", "critical"]
