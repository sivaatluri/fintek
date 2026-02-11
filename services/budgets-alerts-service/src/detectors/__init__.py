"""
Detectors for budget monitoring.
"""

from .base import BaseDetector
from .threshold_detector import BudgetThresholdDetector
from .forecast_detector import ForecastDetector
from .anomaly_detector import AnomalyDetector

# Detector registry
DETECTOR_REGISTRY = {
    "budget_threshold": BudgetThresholdDetector,
    "forecast": ForecastDetector,
    "anomaly": AnomalyDetector,
}

__all__ = [
    "BaseDetector",
    "BudgetThresholdDetector",
    "ForecastDetector",
    "AnomalyDetector",
    "DETECTOR_REGISTRY",
]
