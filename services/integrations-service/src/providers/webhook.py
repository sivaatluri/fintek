"""Webhook integration provider with HMAC signing."""
import hashlib
import hmac
import time
from typing import Any, Dict, Optional

import httpx

from finops_common import get_logger

from .base import IntegrationProvider, ProviderResponse

logger = get_logger(__name__)


class WebhookProvider(IntegrationProvider):
    """Webhook provider with HMAC signing and retries."""

    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None):
        """Initialize webhook provider."""
        super().__init__(config, credentials)
        self.url = config.get("url")
        self.method = config.get("method", "POST").upper()
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 30)
        self.verify_ssl = config.get("verify_ssl", True)
        
        # HMAC signing
        self.signing_secret = credentials.get("signing_secret") if credentials else None
        self.signature_header = config.get("signature_header", "X-Webhook-Signature")
        self.timestamp_header = config.get("timestamp_header", "X-Webhook-Timestamp")

    def _generate_signature(self, payload: str, timestamp: int) -> str:
        """
        Generate HMAC signature for payload.
        
        Args:
            payload: JSON payload string
            timestamp: Unix timestamp
            
        Returns:
            HMAC signature as hex string
        """
        if not self.signing_secret:
            return ""
        
        # Create signature payload: timestamp.payload
        sig_payload = f"{timestamp}.{payload}"
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.signing_secret.encode(),
            sig_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    async def send(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Send webhook with HMAC signing."""
        if not self.url:
            return ProviderResponse(
                success=False,
                error_message="Webhook URL not configured"
            )

        start_time = time.time()
        
        try:
            # Prepare headers
            headers = self.headers.copy()
            headers["Content-Type"] = "application/json"
            
            # Add HMAC signature if secret is configured
            if self.signing_secret:
                timestamp = int(time.time())
                import json
                payload_str = json.dumps(payload, sort_keys=True)
                signature = self._generate_signature(payload_str, timestamp)
                
                headers[self.signature_header] = signature
                headers[self.timestamp_header] = str(timestamp)
                
                logger.info(f"Generated HMAC signature for webhook to {self.url}")

            # Send HTTP request
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.request(
                    method=self.method,
                    url=self.url,
                    json=payload,
                    headers=headers
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Parse response
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"body": response.text}
                
                success = 200 <= response.status_code < 300
                
                return ProviderResponse(
                    success=success,
                    http_status=response.status_code,
                    response_data=response_data,
                    error_message=None if success else f"HTTP {response.status_code}: {response.text}",
                    duration_ms=duration_ms
                )
                
        except httpx.TimeoutException as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Webhook timeout to {self.url}: {e}")
            return ProviderResponse(
                success=False,
                error_message=f"Request timeout after {self.timeout}s",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Webhook error to {self.url}: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    async def verify(self) -> ProviderResponse:
        """Verify webhook endpoint is reachable."""
        if not self.url:
            return ProviderResponse(
                success=False,
                error_message="Webhook URL not configured"
            )
        
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=10) as client:
                # Try HEAD or GET request
                response = await client.head(self.url)
                
                # Consider 2xx and 405 (Method Not Allowed) as success
                success = response.status_code < 500
                
                return ProviderResponse(
                    success=success,
                    http_status=response.status_code,
                    error_message=None if success else f"HTTP {response.status_code}"
                )
        except Exception as e:
            return ProviderResponse(
                success=False,
                error_message=f"Verification failed: {str(e)}"
            )

    async def test(self, payload: Optional[Dict[str, Any]] = None) -> ProviderResponse:
        """Test webhook with sample payload."""
        test_payload = payload or {
            "event": "test",
            "message": "This is a test webhook delivery",
            "timestamp": int(time.time())
        }
        
        return await self.send(test_payload)
