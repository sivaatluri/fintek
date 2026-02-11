"""Tests for delivery retry logic."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.crud.delivery_manager import DeliveryManager
from src.crud.integrations import IntegrationCRUD
from src.models import DeliveryStatus, IntegrationType


class TestRetryLogic:
    """Test delivery retry logic."""

    @pytest.mark.asyncio
    async def test_create_delivery(self, db_session, sample_org_id):
        """Test creating a delivery record."""
        # Create integration first
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        # Create delivery
        payload = {"event": "test", "data": "value"}
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload=payload,
            max_attempts=3
        )
        
        assert delivery is not None
        assert delivery.integration_id == integration.id
        assert delivery.org_id == sample_org_id
        assert delivery.status == DeliveryStatus.PENDING
        assert delivery.payload == payload
        assert delivery.attempts == 0
        assert delivery.max_attempts == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, db_session, sample_org_id):
        """Test exponential backoff for retry delays."""
        # Create integration
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        # Create delivery
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test"},
            max_attempts=5
        )
        
        # Mock provider to always fail
        with patch('src.crud.delivery_manager.get_provider') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.send = AsyncMock(return_value=AsyncMock(
                success=False,
                error_message="Connection refused"
            ))
            mock_provider.return_value = mock_instance
            
            # Attempt 1
            await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            
            assert delivery.attempts == 1
            assert delivery.status == DeliveryStatus.RETRYING
            assert delivery.next_retry_at is not None
            
            # Verify backoff: 2^1 = 2 minutes
            expected_retry = datetime.utcnow() + timedelta(minutes=2)
            time_diff = abs((delivery.next_retry_at - expected_retry).total_seconds())
            assert time_diff < 5  # Allow 5 second tolerance
            
            first_retry_time = delivery.next_retry_at
            
            # Attempt 2
            await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            
            assert delivery.attempts == 2
            assert delivery.status == DeliveryStatus.RETRYING
            
            # Verify backoff: 2^2 = 4 minutes
            expected_retry = datetime.utcnow() + timedelta(minutes=4)
            time_diff = abs((delivery.next_retry_at - expected_retry).total_seconds())
            assert time_diff < 5
            
            # Verify retry time increased
            assert delivery.next_retry_at > first_retry_time

    @pytest.mark.asyncio
    async def test_max_attempts_reached(self, db_session, sample_org_id):
        """Test that delivery fails after max attempts."""
        # Create integration
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        # Create delivery with max 3 attempts
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test"},
            max_attempts=3
        )
        
        # Mock provider to always fail
        with patch('src.crud.delivery_manager.get_provider') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.send = AsyncMock(return_value=AsyncMock(
                success=False,
                error_message="Connection refused"
            ))
            mock_provider.return_value = mock_instance
            
            # Attempt 1
            result1 = await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            assert result1 is False
            assert delivery.attempts == 1
            assert delivery.status == DeliveryStatus.RETRYING
            
            # Attempt 2
            result2 = await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            assert result2 is False
            assert delivery.attempts == 2
            assert delivery.status == DeliveryStatus.RETRYING
            
            # Attempt 3 - should fail permanently
            result3 = await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            assert result3 is False
            assert delivery.attempts == 3
            assert delivery.status == DeliveryStatus.FAILED
            assert delivery.next_retry_at is None  # No more retries

    @pytest.mark.asyncio
    async def test_successful_delivery_resets_status(self, db_session, sample_org_id):
        """Test that successful delivery sets correct status."""
        # Create integration
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        # Create delivery
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test"}
        )
        
        # Mock provider to succeed
        with patch('src.crud.delivery_manager.get_provider') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.send = AsyncMock(return_value=AsyncMock(
                success=True,
                response_data={"id": "12345"},
                http_status=200,
                duration_ms=150
            ))
            mock_provider.return_value = mock_instance
            
            result = await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            
            assert result is True
            assert delivery.status == DeliveryStatus.DELIVERED
            assert delivery.delivered_at is not None
            assert delivery.response == {"id": "12345"}
            assert delivery.http_status == 200
            assert delivery.error_message is None
            assert delivery.next_retry_at is None

    @pytest.mark.asyncio
    async def test_get_pending_retries(self, db_session, sample_org_id):
        """Test getting deliveries due for retry."""
        # Create integration
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        # Create delivery 1 - due now
        delivery1 = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test1"}
        )
        delivery1.status = DeliveryStatus.RETRYING
        delivery1.next_retry_at = datetime.utcnow() - timedelta(minutes=1)  # Past
        await db_session.flush()
        
        # Create delivery 2 - due in future
        delivery2 = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test2"}
        )
        delivery2.status = DeliveryStatus.RETRYING
        delivery2.next_retry_at = datetime.utcnow() + timedelta(hours=1)  # Future
        await db_session.flush()
        
        # Create delivery 3 - failed (not retrying)
        delivery3 = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test3"}
        )
        delivery3.status = DeliveryStatus.FAILED
        await db_session.flush()
        
        # Get pending retries
        pending = await DeliveryManager.get_pending_retries(db_session, limit=10)
        
        # Only delivery1 should be returned
        assert len(pending) == 1
        assert pending[0].id == delivery1.id

    @pytest.mark.asyncio
    async def test_integration_failure_count(self, db_session, sample_org_id):
        """Test that integration failure count is tracked."""
        # Create integration
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        assert integration.failure_count == 0
        
        # Create delivery
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test"}
        )
        
        # Mock provider to fail
        with patch('src.crud.delivery_manager.get_provider') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.send = AsyncMock(return_value=AsyncMock(
                success=False,
                error_message="Error"
            ))
            mock_provider.return_value = mock_instance
            
            # Attempt delivery - should fail
            await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            
            # Check failure count increased
            await db_session.refresh(integration)
            assert integration.failure_count == 1

    @pytest.mark.asyncio
    async def test_integration_failure_count_reset_on_success(self, db_session, sample_org_id):
        """Test that failure count resets on successful delivery."""
        # Create integration with existing failure count
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        integration.failure_count = 5
        await db_session.flush()
        
        # Create delivery
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test"}
        )
        
        # Mock provider to succeed
        with patch('src.crud.delivery_manager.get_provider') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.send = AsyncMock(return_value=AsyncMock(
                success=True,
                response_data={"success": True}
            ))
            mock_provider.return_value = mock_instance
            
            # Attempt delivery - should succeed
            await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            
            # Check failure count reset
            await db_session.refresh(integration)
            assert integration.failure_count == 0

    @pytest.mark.asyncio
    async def test_delivery_duration_tracking(self, db_session, sample_org_id):
        """Test that delivery duration is tracked."""
        # Create integration
        integration = await IntegrationCRUD.create(
            db=db_session,
            org_id=sample_org_id,
            name="Test Webhook",
            integration_type=IntegrationType.WEBHOOK,
            config={"url": "https://example.com/webhook"}
        )
        
        # Create delivery
        delivery = await DeliveryManager.create_delivery(
            db=db_session,
            integration_id=integration.id,
            org_id=sample_org_id,
            payload={"event": "test"}
        )
        
        # Mock provider with duration
        with patch('src.crud.delivery_manager.get_provider') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.send = AsyncMock(return_value=AsyncMock(
                success=True,
                duration_ms=250
            ))
            mock_provider.return_value = mock_instance
            
            await DeliveryManager.attempt_delivery(db_session, delivery.id, sample_org_id)
            await db_session.refresh(delivery)
            
            assert delivery.duration_ms == 250
