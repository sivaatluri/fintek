"""Tests for escalation engine."""
import pytest
from engine.escalation import EscalationEngine


def test_duration_escalation():
    """Test duration-based escalation."""
    engine = EscalationEngine()
    
    escalation_rules = {
        "rules": [
            {
                "name": "Escalate to manager",
                "trigger_type": "duration",
                "duration_minutes": 60,
                "actions": [
                    {"type": "email", "to": "manager@example.com"},
                ],
            },
        ],
    }
    
    # Should not escalate before threshold
    actions = engine.get_escalation_actions(escalation_rules, 30, 0)
    assert len(actions) == 0
    
    # Should escalate after threshold
    actions = engine.get_escalation_actions(escalation_rules, 90, 0)
    assert len(actions) == 1
    assert actions[0]["type"] == "email"


def test_retry_escalation():
    """Test retry-based escalation."""
    engine = EscalationEngine()
    
    escalation_rules = {
        "rules": [
            {
                "name": "Escalate after retries",
                "trigger_type": "retry",
                "retry_count": 2,
                "actions": [
                    {"type": "pagerduty", "severity": "high"},
                ],
            },
        ],
    }
    
    # Should not escalate before retry threshold
    actions = engine.get_escalation_actions(escalation_rules, 10, 1)
    assert len(actions) == 0
    
    # Should escalate after retry threshold
    actions = engine.get_escalation_actions(escalation_rules, 10, 3)
    assert len(actions) == 1
    assert actions[0]["type"] == "pagerduty"


def test_multiple_escalation_rules():
    """Test multiple escalation rules."""
    engine = EscalationEngine()
    
    escalation_rules = {
        "rules": [
            {
                "name": "First escalation",
                "trigger_type": "duration",
                "duration_minutes": 30,
                "actions": [{"type": "slack"}],
            },
            {
                "name": "Second escalation",
                "trigger_type": "duration",
                "duration_minutes": 60,
                "actions": [{"type": "email"}],
            },
        ],
    }
    
    # Should trigger both rules
    actions = engine.get_escalation_actions(escalation_rules, 90, 0)
    assert len(actions) == 2
