"""Tests for deduplication and idempotency."""
import pytest
from engine.idempotency import IdempotencyChecker


def test_dedupe_key_generation():
    """Test dedupe key generation."""
    checker = IdempotencyChecker(None)
    
    key1 = checker.generate_dedupe_key(
        org_id="org-123",
        event_type="budget.threshold_exceeded",
        scope={"budget_id": "budget-456"},
        period="monthly",
        threshold=80,
        workflow_version=1,
    )
    
    # Same inputs should generate same key
    key2 = checker.generate_dedupe_key(
        org_id="org-123",
        event_type="budget.threshold_exceeded",
        scope={"budget_id": "budget-456"},
        period="monthly",
        threshold=80,
        workflow_version=1,
    )
    
    assert key1 == key2
    assert len(key1) == 64  # SHA256 produces 64 hex characters


def test_dedupe_key_uniqueness():
    """Test that different inputs generate different keys."""
    checker = IdempotencyChecker(None)
    
    key1 = checker.generate_dedupe_key(
        org_id="org-123",
        event_type="budget.threshold_exceeded",
        scope={"budget_id": "budget-456"},
    )
    
    # Different budget should generate different key
    key2 = checker.generate_dedupe_key(
        org_id="org-123",
        event_type="budget.threshold_exceeded",
        scope={"budget_id": "budget-789"},
    )
    
    assert key1 != key2


def test_dedupe_key_version_sensitivity():
    """Test that workflow version affects dedupe key."""
    checker = IdempotencyChecker(None)
    
    key1 = checker.generate_dedupe_key(
        org_id="org-123",
        event_type="budget.threshold_exceeded",
        workflow_version=1,
    )
    
    key2 = checker.generate_dedupe_key(
        org_id="org-123",
        event_type="budget.threshold_exceeded",
        workflow_version=2,
    )
    
    assert key1 != key2
