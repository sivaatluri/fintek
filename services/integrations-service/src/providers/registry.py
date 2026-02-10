"""Provider registry for managing integration providers."""
from typing import Any, Dict, Optional, Type

from finops_common import get_logger

from ..models import IntegrationType
from .base import IntegrationProvider
from .email import EmailProvider
from .jira import JiraProvider
from .servicenow import ServiceNowProvider
from .webhook import WebhookProvider

logger = get_logger(__name__)


class ProviderRegistry:
    """Registry for integration providers."""
    
    _providers: Dict[IntegrationType, Type[IntegrationProvider]] = {
        IntegrationType.WEBHOOK: WebhookProvider,
        IntegrationType.EMAIL: EmailProvider,
        IntegrationType.JIRA: JiraProvider,
        IntegrationType.SERVICENOW: ServiceNowProvider,
    }
    
    @classmethod
    def register(cls, integration_type: IntegrationType, provider_class: Type[IntegrationProvider]) -> None:
        """
        Register a provider for an integration type.
        
        Args:
            integration_type: Type of integration
            provider_class: Provider class to register
        """
        cls._providers[integration_type] = provider_class
        logger.info(f"Registered provider {provider_class.__name__} for {integration_type.value}")
    
    @classmethod
    def get_provider(
        cls,
        integration_type: IntegrationType,
        config: Dict[str, Any],
        credentials: Optional[Dict[str, Any]] = None
    ) -> IntegrationProvider:
        """
        Get provider instance for integration type.
        
        Args:
            integration_type: Type of integration
            config: Provider configuration
            credentials: Optional credentials
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider not found for integration type
        """
        provider_class = cls._providers.get(integration_type)
        
        if not provider_class:
            raise ValueError(f"No provider registered for integration type: {integration_type.value}")
        
        return provider_class(config=config, credentials=credentials)
    
    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """List all registered providers."""
        return {
            integration_type.value: provider_class.__name__
            for integration_type, provider_class in cls._providers.items()
        }


def get_provider(
    integration_type: IntegrationType,
    config: Dict[str, Any],
    credentials: Optional[Dict[str, Any]] = None
) -> IntegrationProvider:
    """
    Convenience function to get a provider instance.
    
    Args:
        integration_type: Type of integration
        config: Provider configuration
        credentials: Optional credentials
        
    Returns:
        Provider instance
    """
    return ProviderRegistry.get_provider(integration_type, config, credentials)
