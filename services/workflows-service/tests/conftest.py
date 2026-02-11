"""Test configuration and fixtures."""
import pytest
from datetime import datetime
from uuid import uuid4

@pytest.fixture
def sample_budget_event():
    """Sample budget exceeded event."""
    return {
        "event_id": str(uuid4()),
        "event_type": "budget.threshold_exceeded",
        "event_version": "1.0.0",
        "tenant_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "source": {
            "service": "budgets-alerts-service",
            "instance": "instance-1",
        },
        "payload": {
            "budget_id": str(uuid4()),
            "budget_name": "Production Budget",
            "period": "monthly",
            "threshold_type": "percentage",
            "threshold_value": 80,
            "threshold_percentage": 80,
            "current_spend": 85000,
            "budget_amount": 100000,
            "currency": "USD",
            "period_start": "2024-01-01",
            "period_end": "2024-01-31",
            "scope": {
                "type": "account",
                "value": "aws-prod-account",
            },
        },
    }

@pytest.fixture
def sample_anomaly_event():
    """Sample anomaly event."""
    return {
        "event_id": str(uuid4()),
        "event_type": "anomaly.cost_spike",
        "event_version": "1.0.0",
        "tenant_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "source": {
            "service": "budgets-alerts-service",
            "instance": "instance-1",
        },
        "payload": {
            "anomaly_id": str(uuid4()),
            "anomaly_type": "cost_spike",
            "severity": "high",
            "detected_at": datetime.utcnow().isoformat(),
            "detection_method": "statistical",
            "confidence_score": 0.95,
            "current_value": 15000,
            "expected_value": 5000,
            "deviation_percentage": 200,
            "currency": "USD",
            "resource_id": "i-1234567890",
            "service": "EC2",
            "region": "us-east-1",
        },
    }

@pytest.fixture
def sample_workflow_definition():
    """Sample workflow definition."""
    return {
        "name": "Budget Alert Workflow",
        "trigger_type": "event",
        "trigger_config": {
            "event_types": ["budget.threshold_exceeded"],
        },
        "conditions": {
            "logic": "and",
            "rules": [
                {
                    "field": "payload.threshold_percentage",
                    "operator": "gte",
                    "value": 80,
                },
            ],
        },
        "actions": [
            {
                "name": "Create Jira Issue",
                "type": "jira",
                "template": "budget_exceeded",
                "integration": "jira-prod",
                "required": True,
            },
            {
                "name": "Send Slack Message",
                "type": "slack",
                "template": "budget_exceeded",
                "integration": "slack-finops",
                "required": False,
            },
        ],
        "dedupe_config": {
            "scope_fields": ["budget_id"],
            "cooldown_minutes": 60,
        },
    }
