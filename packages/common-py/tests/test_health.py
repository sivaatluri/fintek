"""Tests for health checker."""
import pytest

from finops_common.health import HealthChecker


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check."""
    checker = HealthChecker("test-service", "1.0.0")
    response = await checker.health()

    assert response.status == "healthy"
    assert response.service == "test-service"
    assert response.version == "1.0.0"
    assert response.timestamp is not None


@pytest.mark.asyncio
async def test_ready_check_no_checks():
    """Test readiness check with no registered checks."""
    checker = HealthChecker("test-service", "1.0.0")
    response = await checker.ready()

    assert response.ready is True
    assert response.service == "test-service"
    assert response.version == "1.0.0"
    assert response.checks == {}


@pytest.mark.asyncio
async def test_ready_check_with_passing_checks():
    """Test readiness check with passing checks."""
    checker = HealthChecker("test-service", "1.0.0")

    async def db_check():
        return True

    async def cache_check():
        return {"status": "ready", "info": "Connected"}

    checker.register_ready_check("database", db_check)
    checker.register_ready_check("cache", cache_check)

    response = await checker.ready()

    assert response.ready is True
    assert "database" in response.checks
    assert response.checks["database"]["status"] == "ready"
    assert "cache" in response.checks
    assert response.checks["cache"]["status"] == "ready"


@pytest.mark.asyncio
async def test_ready_check_with_failing_checks():
    """Test readiness check with failing checks."""
    checker = HealthChecker("test-service", "1.0.0")

    async def passing_check():
        return True

    async def failing_check():
        return False

    checker.register_ready_check("passing", passing_check)
    checker.register_ready_check("failing", failing_check)

    response = await checker.ready()

    assert response.ready is False
    assert response.checks["passing"]["status"] == "ready"
    assert response.checks["failing"]["status"] == "not_ready"


@pytest.mark.asyncio
async def test_ready_check_with_exception():
    """Test readiness check when check raises exception."""
    checker = HealthChecker("test-service", "1.0.0")

    async def error_check():
        raise ValueError("Connection failed")

    checker.register_ready_check("error", error_check)

    response = await checker.ready()

    assert response.ready is False
    assert response.checks["error"]["status"] == "error"
    assert "Connection failed" in response.checks["error"]["error"]
