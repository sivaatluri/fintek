"""
Base connector interface for cost ingestion.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date


class BaseConnector(ABC):
    """Base class for all cost connectors"""
    
    def __init__(self, org_id: str, config: Dict[str, Any]):
        """
        Initialize connector.
        
        Args:
            org_id: Organization ID
            config: Connector-specific configuration
        """
        self.org_id = org_id
        self.config = config
    
    @abstractmethod
    async def fetch_data(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch cost data from the data source.
        
        Args:
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            List of raw cost records following raw_cost.schema.json
        """
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """
        Validate connector configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    def get_connector_type(self) -> str:
        """Get connector type identifier"""
        return self.__class__.__name__.replace("Connector", "").lower()
