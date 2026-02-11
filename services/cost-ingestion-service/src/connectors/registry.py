"""
Connector registry for dynamic connector management.
"""

from typing import Dict, Type, Optional
from .base import BaseConnector


class ConnectorRegistry:
    """Registry for managing available connectors"""
    
    def __init__(self):
        self._connectors: Dict[str, Type[BaseConnector]] = {}
    
    def register(self, connector_type: str, connector_class: Type[BaseConnector]):
        """
        Register a connector.
        
        Args:
            connector_type: Unique identifier for the connector
            connector_class: Connector class implementing BaseConnector
        """
        self._connectors[connector_type] = connector_class
    
    def get(self, connector_type: str) -> Optional[Type[BaseConnector]]:
        """
        Get a connector class by type.
        
        Args:
            connector_type: Connector type identifier
            
        Returns:
            Connector class or None if not found
        """
        return self._connectors.get(connector_type)
    
    def list_connectors(self) -> Dict[str, str]:
        """
        List all registered connectors.
        
        Returns:
            Dictionary of connector types and class names
        """
        return {
            connector_type: connector_class.__name__
            for connector_type, connector_class in self._connectors.items()
        }
    
    def create_connector(
        self,
        connector_type: str,
        org_id: str,
        config: dict
    ) -> BaseConnector:
        """
        Create a connector instance.
        
        Args:
            connector_type: Connector type identifier
            org_id: Organization ID
            config: Connector configuration
            
        Returns:
            Connector instance
            
        Raises:
            ValueError: If connector type not found
        """
        connector_class = self.get(connector_type)
        if not connector_class:
            raise ValueError(f"Connector type '{connector_type}' not found")
        
        return connector_class(org_id=org_id, config=config)


# Global connector registry
connector_registry = ConnectorRegistry()
