"""
Anomaly detector - detects cost spikes using baseline analysis.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

from ..models.models import Budget
from .base import BaseDetector, DetectionResult


class AnomalyDetector(BaseDetector):
    """Detects anomalous cost spikes using statistical methods."""
    
    def get_name(self) -> str:
        return "anomaly"
    
    def get_description(self) -> str:
        return "Detects cost spikes using 14-day baseline (mean + 2*stddev)"
    
    async def detect(
        self,
        budget: Budget,
        cost_data: List[Dict[str, Any]],
    ) -> Optional[DetectionResult]:
        """Detect anomalous spikes in cost data."""
        # Need at least 14 days for baseline calculation
        if len(cost_data) < 14:
            return None
        
        # Sort by date
        sorted_data = sorted(cost_data, key=lambda x: x.get("date", datetime.now()))
        
        # Get last 14 days for baseline (excluding most recent day)
        baseline_data = sorted_data[-15:-1]
        current_data = sorted_data[-1]
        
        # Calculate baseline statistics
        baseline_amounts = [item.get("amount", 0) for item in baseline_data]
        baseline_mean = statistics.mean(baseline_amounts)
        
        # Calculate standard deviation
        if len(baseline_amounts) > 1:
            baseline_std = statistics.stdev(baseline_amounts)
        else:
            baseline_std = 0
        
        # Calculate threshold (mean + 2 * stddev)
        threshold = baseline_mean + (2 * baseline_std)
        
        # Get current value
        current_value = current_data.get("amount", 0)
        
        # Check if current value exceeds threshold
        if current_value <= threshold:
            return None
        
        # Calculate how many standard deviations above mean
        if baseline_std > 0:
            stddev_multiplier = (current_value - baseline_mean) / baseline_std
        else:
            stddev_multiplier = 0
        
        # Calculate confidence (0.0 to 1.0)
        # Higher multiplier = higher confidence
        confidence = min(1.0, stddev_multiplier / 10.0)
        
        # Determine severity based on stddev multiplier
        if stddev_multiplier >= 4:
            severity = "critical"
        elif stddev_multiplier >= 3:
            severity = "high"
        elif stddev_multiplier >= 2:
            severity = "medium"
        else:
            severity = "low"
        
        message = (
            f"Anomalous cost spike detected for budget '{budget.name}'. "
            f"Current: ${current_value:,.2f}, "
            f"Baseline: ${baseline_mean:,.2f} "
            f"({stddev_multiplier:.1f}σ above mean)"
        )
        
        details = {
            "current_value": round(current_value, 2),
            "baseline_mean": round(baseline_mean, 2),
            "baseline_std": round(baseline_std, 2),
            "threshold": round(threshold, 2),
            "stddev_multiplier": round(stddev_multiplier, 2),
            "confidence": round(confidence, 3),
            "baseline_days": 14,
        }
        
        return DetectionResult(
            detected=True,
            severity=severity,
            message=message,
            details=details,
        )
