"""Escalation rules implementation."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from finops_common import get_logger

logger = get_logger(__name__)


class EscalationEngine:
    """Handles workflow escalation rules."""
    
    def __init__(self):
        pass
    
    def get_escalation_actions(
        self,
        escalation_rules: Optional[Dict],
        execution_duration_minutes: int,
        retry_count: int = 0,
    ) -> List[Dict]:
        """Get escalation actions based on rules and execution state."""
        if not escalation_rules:
            return []
        
        actions = []
        rules = escalation_rules.get("rules", [])
        
        for rule in rules:
            if self._should_escalate(rule, execution_duration_minutes, retry_count):
                escalation_actions = rule.get("actions", [])
                actions.extend(escalation_actions)
                logger.info(
                    f"Escalation triggered: {rule.get('name')} "
                    f"(duration: {execution_duration_minutes}m, retries: {retry_count})"
                )
        
        return actions
    
    def _should_escalate(
        self,
        rule: Dict,
        duration_minutes: int,
        retry_count: int,
    ) -> bool:
        """Check if escalation rule should trigger."""
        trigger_type = rule.get("trigger_type", "duration")
        
        if trigger_type == "duration":
            threshold = rule.get("duration_minutes", 60)
            return duration_minutes >= threshold
        
        elif trigger_type == "retry":
            threshold = rule.get("retry_count", 2)
            return retry_count >= threshold
        
        elif trigger_type == "failure_rate":
            # Not yet implemented
            return False
        
        return False
    
    def apply_delay(
        self,
        action: Dict,
        current_time: Optional[datetime] = None,
    ) -> datetime:
        """Calculate delay for escalation action."""
        if not current_time:
            current_time = datetime.utcnow()
        
        delay_minutes = action.get("delay_minutes", 0)
        return current_time + timedelta(minutes=delay_minutes)
