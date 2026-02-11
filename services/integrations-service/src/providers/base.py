"""Base integration provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProviderResponse:
    """Response from a provider delivery attempt."""
    success: bool
    http_status: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    duration_ms: Optional[int] = None


class IntegrationProvider(ABC):
    """Base class for integration providers."""

    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None):
        """Initialize provider with configuration."""
        self.config = config
        self.credentials = credentials or {}

    @abstractmethod
    async def send(self, payload: Dict[str, Any]) -> ProviderResponse:
        """
        Send data via this integration.
        
        Args:
            payload: Data to send
            
        Returns:
            ProviderResponse with delivery results
        """
        pass

    @abstractmethod
    async def verify(self) -> ProviderResponse:
        """
        Verify that the integration is configured correctly.
        
        Returns:
            ProviderResponse with verification results
        """
        pass

    @abstractmethod
    async def test(self, payload: Optional[Dict[str, Any]] = None) -> ProviderResponse:
        """
        Test the integration with sample data.
        
        Args:
            payload: Optional test payload
            
        Returns:
            ProviderResponse with test results
        """
        pass
