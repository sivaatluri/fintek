"""
Forecast detector - predicts if spend will exceed budget using linear regression.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics

from ..models.models import Budget
from .base import BaseDetector, DetectionResult


class ForecastDetector(BaseDetector):
    """Forecasts future spend and alerts if budget will be exceeded."""
    
    def get_name(self) -> str:
        return "forecast"
    
    def get_description(self) -> str:
        return "Forecasts spend to end of period using linear regression"
    
    def _calculate_linear_regression(self, data_points: List[tuple]) -> tuple:
        """
        Calculate linear regression (y = mx + b).
        
        Args:
            data_points: List of (x, y) tuples
            
        Returns:
            Tuple of (slope, intercept, r_squared)
        """
        if len(data_points) < 2:
            return 0, 0, 0
        
        n = len(data_points)
        x_values = [p[0] for p in data_points]
        y_values = [p[1] for p in data_points]
        
        # Calculate means
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        
        # Calculate slope (m)
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in data_points)
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0, y_mean, 0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        y_pred = [slope * x + intercept for x in x_values]
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        ss_res = sum((y - y_p) ** 2 for y, y_p in zip(y_values, y_pred))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return slope, intercept, r_squared
    
    async def detect(
        self,
        budget: Budget,
        cost_data: List[Dict[str, Any]],
    ) -> Optional[DetectionResult]:
        """Forecast spend and check if budget will be exceeded."""
        # Need at least 7 days of data for meaningful forecast
        if len(cost_data) < 7:
            return None
        
        # Sort by date
        sorted_data = sorted(cost_data, key=lambda x: x.get("date", datetime.now()))
        
        # Convert to data points (days from start, cumulative spend)
        start_date = sorted_data[0].get("date")
        cumulative_spend = 0
        data_points = []
        
        for item in sorted_data:
            date = item.get("date", datetime.now())
            amount = item.get("amount", 0)
            cumulative_spend += amount
            
            # Days from start
            if isinstance(date, datetime):
                days = (date - start_date).days
            else:
                days = len(data_points)
            
            data_points.append((days, cumulative_spend))
        
        # Calculate linear regression
        slope, intercept, r_squared = self._calculate_linear_regression(data_points)
        
        # Calculate days until budget end
        if isinstance(budget.end_date, datetime) and isinstance(start_date, datetime):
            days_until_end = (budget.end_date - start_date).days
        else:
            # Default to 30 days for monthly budget
            days_until_end = 30
        
        # Forecast spend at end of period
        forecast_spend = slope * days_until_end + intercept
        
        # Check if forecast exceeds budget
        if forecast_spend <= budget.amount:
            return None
        
        # Calculate confidence based on R-squared
        confidence = r_squared
        
        # Determine severity based on how much forecast exceeds budget
        overage_percentage = ((forecast_spend - budget.amount) / budget.amount) * 100
        
        if overage_percentage >= 50:
            severity = "critical"
        elif overage_percentage >= 25:
            severity = "high"
        elif overage_percentage >= 10:
            severity = "medium"
        else:
            severity = "low"
        
        message = (
            f"Budget '{budget.name}' forecast to exceed by "
            f"${forecast_spend - budget.amount:,.2f} "
            f"({overage_percentage:.1f}%). "
            f"Projected: ${forecast_spend:,.2f}, Budget: ${budget.amount:,.2f}"
        )
        
        details = {
            "forecast_amount": round(forecast_spend, 2),
            "budget_amount": budget.amount,
            "overage_amount": round(forecast_spend - budget.amount, 2),
            "overage_percentage": round(overage_percentage, 2),
            "confidence": round(confidence, 3),
            "r_squared": round(r_squared, 3),
            "trend_slope": round(slope, 2),
        }
        
        return DetectionResult(
            detected=True,
            severity=severity,
            message=message,
            details=details,
        )
