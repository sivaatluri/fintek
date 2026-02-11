"""Tests for condition evaluator."""
import pytest
from engine.evaluator import ConditionEvaluator


def test_simple_equality():
    """Test simple equality condition."""
    evaluator = ConditionEvaluator()
    
    event = {"payload": {"threshold": 80}}
    condition = {
        "logic": "and",
        "rules": [
            {"field": "payload.threshold", "operator": "eq", "value": 80}
        ],
    }
    
    assert evaluator.evaluate(condition, event)


def test_comparison_operators():
    """Test comparison operators."""
    evaluator = ConditionEvaluator()
    
    event = {"payload": {"value": 100}}
    
    # Greater than
    condition_gt = {
        "logic": "and",
        "rules": [
            {"field": "payload.value", "operator": "gt", "value": 50}
        ],
    }
    assert evaluator.evaluate(condition_gt, event)
    
    # Less than or equal
    condition_lte = {
        "logic": "and",
        "rules": [
            {"field": "payload.value", "operator": "lte", "value": 100}
        ],
    }
    assert evaluator.evaluate(condition_lte, event)


def test_nested_conditions():
    """Test nested AND/OR conditions."""
    evaluator = ConditionEvaluator()
    
    event = {
        "payload": {
            "severity": "high",
            "value": 100,
        }
    }
    
    condition = {
        "logic": "and",
        "rules": [
            {"field": "payload.severity", "operator": "eq", "value": "high"},
            {
                "logic": "or",
                "rules": [
                    {"field": "payload.value", "operator": "gt", "value": 50},
                    {"field": "payload.value", "operator": "lt", "value": 10},
                ],
            },
        ],
    }
    
    assert evaluator.evaluate(condition, event)


def test_string_operators():
    """Test string-specific operators."""
    evaluator = ConditionEvaluator()
    
    event = {"payload": {"message": "budget threshold exceeded"}}
    
    # Contains
    condition_contains = {
        "logic": "and",
        "rules": [
            {"field": "payload.message", "operator": "contains", "value": "budget"}
        ],
    }
    assert evaluator.evaluate(condition_contains, event)
    
    # Starts with
    condition_starts = {
        "logic": "and",
        "rules": [
            {"field": "payload.message", "operator": "startswith", "value": "budget"}
        ],
    }
    assert evaluator.evaluate(condition_starts, event)
