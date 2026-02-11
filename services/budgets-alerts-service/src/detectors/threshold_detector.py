"""
Budget threshold detector - checks 50/80/90/100% thresholds.
"""

from typing import List, Dict, Any, Optional
from ..models.models import Budget
from .base import BaseDetector, DetectionResult


class BudgetThresholdDetector(BaseDetector):
    """Detects when budget thresholds are exceeded."""
    
    def get_name(self) -> str:
        return "budget_threshold"
    
    def get_description(self) -> str:
        return "Checks if actual spend exceeds budget thresholds (50%, 80%, 90%, 100%)"
    
    async def detect(
        self,
        budget: Budget,
        cost_data: List[Dict[str, Any]],
    ) -> Optional[DetectionResult]:
        """Check if budget threshold is exceeded."""
        # Calculate current spend from cost data
        current_spend = sum(item.get("amount", 0) for item in cost_data)
        
        # Update budget current spend
        budget.current_spend = current_spend
        
        # Calculate percentage
        percentage = (current_spend / budget.amount * 100) if budget.amount > 0 else 0
        
        # Get thresholds (default: [50, 80, 90, 100])
        thresholds = budget.thresholds if budget.thresholds else [50, 80, 90, 100]
        thresholds = sorted(thresholds)
        
        # Get alert state (which thresholds have been triggered)
        alert_state = budget.alert_state if budget.alert_state else {}
        
        # Find highest threshold exceeded that hasn't been alerted
        triggered_threshold = None
        for threshold in reversed(thresholds):
            if percentage >= threshold:
                # Check if already alerted
                threshold_key = f"threshold_{threshold}"
                if not alert_state.get(threshold_key, False):
                    triggered_threshold = threshold
                    break
        
        if triggered_threshold is None:
            return None
        
        # Determine severity based on threshold
        if triggered_threshold >= 100:
            severity = "critical"
        elif triggered_threshold >= 90:
            severity = "high"
        elif triggered_threshold >= 80:
            severity = "medium"
        else:
            severity = "low"
        
        message = (
            f"Budget '{budget.name}' has reached {triggered_threshold}% "
            f"({percentage:.1f}% of ${budget.amount:,.2f}). "
            f"Current spend: ${current_spend:,.2f}"
        )
        
        details = {
            "threshold_percentage": triggered_threshold,
            "actual_percentage": round(percentage, 2),
            "current_spend": current_spend,
            "budget_amount": budget.amount,
        }
        
        # Update alert state
        threshold_key = f"threshold_{triggered_threshold}"
        if alert_state is None:
            alert_state = {}
        alert_state[threshold_key] = True
        budget.alert_state = alert_state
        
        return DetectionResult(
            detected=True,
            severity=severity,
            message=message,
            details=details,
        )
