"""Build execution context from events."""
from typing import Dict

from finops_common import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """Builds workflow execution context."""
    
    def build_context(self, event: Dict, workflow_config: Dict) -> Dict:
        """Build execution context from event and workflow config."""
        context = {
            "event": event,
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "tenant_id": event.get("tenant_id"),
            "timestamp": event.get("timestamp"),
            "payload": event.get("payload", {}),
            "metadata": event.get("metadata", {}),
        }
        
        # Add routing metadata
        routing = self._build_routing_metadata(event)
        context["routing"] = routing
        
        return context
    
    def _build_routing_metadata(self, event: Dict) -> Dict:
        """Build routing metadata for integrations."""
        payload = event.get("payload", {})
        
        routing = {
            "severity": self._extract_severity(event, payload),
            "priority": self._extract_priority(event, payload),
            "assignee": self._extract_assignee(event, payload),
            "labels": self._extract_labels(event, payload),
        }
        
        return routing
    
    def _extract_severity(self, event: Dict, payload: Dict) -> str:
        """Extract severity from event."""
        # Check metadata
        metadata = event.get("metadata", {})
        if "priority" in metadata:
            return metadata["priority"]
        
        # Check payload
        if "severity" in payload:
            return payload["severity"]
        
        # Default based on event type
        event_type = event.get("event_type", "")
        if "critical" in event_type or "exceeded" in event_type:
            return "high"
        elif "warning" in event_type:
            return "medium"
        else:
            return "low"
    
    def _extract_priority(self, event: Dict, payload: Dict) -> str:
        """Extract priority from event."""
        severity_map = {
            "critical": "P1",
            "high": "P2",
            "medium": "P3",
            "low": "P4",
        }
        severity = self._extract_severity(event, payload)
        return severity_map.get(severity, "P3")
    
    def _extract_assignee(self, event: Dict, payload: Dict) -> str:
        """Extract assignee from event."""
        # Could be enhanced with team mapping logic
        return "finops-team"
    
    def _extract_labels(self, event: Dict, payload: Dict) -> list:
        """Extract labels from event."""
        labels = ["finops", "automated"]
        
        event_type = event.get("event_type", "")
        if "budget" in event_type:
            labels.append("budget")
        elif "anomaly" in event_type:
            labels.append("anomaly")
        elif "waste" in event_type:
            labels.append("waste")
        elif "commitment" in event_type:
            labels.append("commitment")
        
        return labels
