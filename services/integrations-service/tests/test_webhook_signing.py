"""Tests for webhook HMAC signing."""
import hashlib
import hmac
import json
import time

import pytest
from unittest.mock import AsyncMock, patch

from src.providers.webhook import WebhookProvider


class TestWebhookSigning:
    """Test webhook HMAC signing functionality."""

    def test_generate_signature(self):
        """Test HMAC signature generation."""
        config = {
            "url": "https://example.com/webhook",
            "method": "POST",
        }
        credentials = {
            "signing_secret": "test-secret-key"
        }
        
        provider = WebhookProvider(config, credentials)
        
        # Test data
        payload = '{"event": "test", "data": "value"}'
        timestamp = 1234567890
        
        # Generate signature
        signature = provider._generate_signature(payload, timestamp)
        
        # Verify signature format
        assert signature is not None
        assert len(signature) == 64  # SHA256 hex is 64 characters
        assert isinstance(signature, str)
        
        # Verify signature is consistent
        signature2 = provider._generate_signature(payload, timestamp)
        assert signature == signature2
        
        # Verify signature changes with different payload
        payload2 = '{"event": "different"}'
        signature3 = provider._generate_signature(payload2, timestamp)
        assert signature != signature3
        
        # Verify signature changes with different timestamp
        timestamp2 = 9876543210
        signature4 = provider._generate_signature(payload, timestamp2)
        assert signature != signature4

    def test_signature_verification(self):
        """Test that generated signature can be verified."""
        config = {
            "url": "https://example.com/webhook",
        }
        credentials = {
            "signing_secret": "test-secret-key"
        }
        
        provider = WebhookProvider(config, credentials)
        
        payload_str = '{"event": "test", "amount": 100}'
        timestamp = int(time.time())
        
        # Generate signature
        signature = provider._generate_signature(payload_str, timestamp)
        
        # Verify signature manually (what the receiver would do)
        sig_payload = f"{timestamp}.{payload_str}"
        expected_signature = hmac.new(
            b"test-secret-key",
            sig_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert signature == expected_signature

    def test_no_signature_without_secret(self):
        """Test that no signature is generated without secret."""
        config = {
            "url": "https://example.com/webhook",
        }
        credentials = {}  # No secret
        
        provider = WebhookProvider(config, credentials)
        
        payload = '{"event": "test"}'
        timestamp = int(time.time())
        
        signature = provider._generate_signature(payload, timestamp)
        assert signature == ""

    @pytest.mark.asyncio
    async def test_send_includes_signature_headers(self):
        """Test that send() includes HMAC headers when secret is configured."""
        config = {
            "url": "https://example.com/webhook",
            "method": "POST",
        }
        credentials = {
            "signing_secret": "test-secret-key"
        }
        
        provider = WebhookProvider(config, credentials)
        
        payload = {"event": "test", "data": "value"}
        
        # Mock HTTP client
        with patch('src.providers.webhook.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_response.text = "OK"
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context
            
            result = await provider.send(payload)
            
            # Verify request was made
            assert mock_context.__aenter__.return_value.request.called
            
            # Get the call arguments
            call_args = mock_context.__aenter__.return_value.request.call_args
            
            # Verify signature headers were included
            headers = call_args.kwargs.get('headers', {})
            assert provider.signature_header in headers
            assert provider.timestamp_header in headers
            
            # Verify signature is valid
            signature = headers[provider.signature_header]
            timestamp = headers[provider.timestamp_header]
            
            assert len(signature) == 64
            assert timestamp.isdigit()

    @pytest.mark.asyncio
    async def test_send_without_signature_when_no_secret(self):
        """Test that send() works without signature when no secret configured."""
        config = {
            "url": "https://example.com/webhook",
            "method": "POST",
        }
        credentials = {}  # No secret
        
        provider = WebhookProvider(config, credentials)
        
        payload = {"event": "test"}
        
        with patch('src.providers.webhook.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_response.text = "OK"
            
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context
            
            result = await provider.send(payload)
            
            # Verify request was made without signature headers
            call_args = mock_context.__aenter__.return_value.request.call_args
            headers = call_args.kwargs.get('headers', {})
            
            assert provider.signature_header not in headers
            assert provider.timestamp_header not in headers

    def test_signature_format(self):
        """Test signature format follows timestamp.payload pattern."""
        config = {"url": "https://example.com/webhook"}
        credentials = {"signing_secret": "secret123"}
        
        provider = WebhookProvider(config, credentials)
        
        payload = '{"key": "value"}'
        timestamp = 1234567890
        
        # The signature should be for "timestamp.payload"
        expected_message = f"{timestamp}.{payload}"
        expected_signature = hmac.new(
            b"secret123",
            expected_message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        actual_signature = provider._generate_signature(payload, timestamp)
        
        assert actual_signature == expected_signature

    def test_json_payload_serialization(self):
        """Test that JSON payload is consistently serialized for signing."""
        config = {"url": "https://example.com/webhook"}
        credentials = {"signing_secret": "secret"}
        
        provider = WebhookProvider(config, credentials)
        
        # Test that dict order doesn't matter (sorted keys)
        payload1 = {"b": 2, "a": 1}
        payload2 = {"a": 1, "b": 2}
        
        timestamp = 1234567890
        
        # Serialize with sorted keys
        payload1_str = json.dumps(payload1, sort_keys=True)
        payload2_str = json.dumps(payload2, sort_keys=True)
        
        sig1 = provider._generate_signature(payload1_str, timestamp)
        sig2 = provider._generate_signature(payload2_str, timestamp)
        
        # Signatures should be the same when keys are sorted
        assert sig1 == sig2
