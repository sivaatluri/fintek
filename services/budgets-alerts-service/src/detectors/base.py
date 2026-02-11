"""
Base detector class for budget monitoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Budget, BudgetAlert


class DetectionResult:
    """Result from a detector run."""
    
    def __init__(
        self,
        detected: bool,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.detected = detected
        self.severity = severity
        self.message = message
        self.details = details or {}


class BaseDetector(ABC):
    """Base class for all detectors."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @abstractmethod
    async def detect(
        self,
        budget: Budget,
        cost_data: List[Dict[str, Any]],
    ) -> Optional[DetectionResult]:
        """
        Run detection on a budget.
        
        Args:
            budget: Budget to check
            cost_data: List of cost data points with 'date' and 'amount' keys
            
        Returns:
            DetectionResult if alert condition met, None otherwise
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get detector name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get detector description."""
        pass
