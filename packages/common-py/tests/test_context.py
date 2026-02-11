"""Tests for request context management."""
import pytest

from finops_common.context import (
    clear_context,
    get_org_id,
    get_request_id,
    get_tenant_id,
    get_user_id,
    set_org_id,
    set_request_id,
    set_tenant_id,
    set_user_id,
)


def test_request_id_context():
    """Test request ID context management."""
    # Set with custom ID
    request_id = set_request_id("test-request-123")
    assert request_id == "test-request-123"
    assert get_request_id() == "test-request-123"

    # Set with auto-generated ID
    request_id = set_request_id()
    assert request_id is not None
    assert len(request_id) == 36  # UUID format
    assert get_request_id() == request_id


def test_org_id_context():
    """Test organization ID context management."""
    set_org_id("org-456")
    assert get_org_id() == "org-456"

    set_org_id(None)
    assert get_org_id() is None


def test_tenant_id_context():
    """Test tenant ID context management."""
    set_tenant_id("tenant-789")
    assert get_tenant_id() == "tenant-789"

    set_tenant_id(None)
    assert get_tenant_id() is None


def test_user_id_context():
    """Test user ID context management."""
    set_user_id("user-101")
    assert get_user_id() == "user-101"

    set_user_id(None)
    assert get_user_id() is None


def test_clear_context():
    """Test clearing all context."""
    set_request_id("test-request")
    set_org_id("test-org")
    set_tenant_id("test-tenant")
    set_user_id("test-user")

    clear_context()

    assert get_request_id() is None
    assert get_org_id() is None
    assert get_tenant_id() is None
    assert get_user_id() is None
