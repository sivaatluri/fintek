"""Condition evaluation for workflows."""
import operator
from typing import Any, Dict

from finops_common import get_logger

logger = get_logger(__name__)


class ConditionEvaluator:
    """Evaluates workflow conditions against events."""
    
    OPERATORS = {
        "eq": operator.eq,
        "ne": operator.ne,
        "gt": operator.gt,
        "gte": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "in": lambda x, y: x in y,
        "not_in": lambda x, y: x not in y,
        "contains": lambda x, y: y in x,
        "startswith": lambda x, y: x.startswith(y) if isinstance(x, str) else False,
        "endswith": lambda x, y: x.endswith(y) if isinstance(x, str) else False,
    }
    
    def evaluate(self, conditions: Dict, event: Dict) -> bool:
        """Evaluate conditions against event."""
        if not conditions:
            return True
        
        logic = conditions.get("logic", "and")
        rules = conditions.get("rules", [])
        
        results = []
        for rule in rules:
            if "rules" in rule:
                # Nested condition
                results.append(self.evaluate(rule, event))
            else:
                # Leaf condition
                results.append(self._evaluate_rule(rule, event))
        
        if logic == "and":
            return all(results) if results else True
        elif logic == "or":
            return any(results) if results else False
        else:
            logger.warning(f"Unknown logic operator: {logic}")
            return False
    
    def _evaluate_rule(self, rule: Dict, event: Dict) -> bool:
        """Evaluate single rule."""
        field = rule.get("field")
        op = rule.get("operator", "eq")
        value = rule.get("value")
        
        # Extract field value from event
        actual = self._get_nested_value(event, field)
        
        # Get operator function
        op_func = self.OPERATORS.get(op)
        if not op_func:
            logger.warning(f"Unknown operator: {op}")
            return False
        
        try:
            result = op_func(actual, value)
            logger.debug(f"Rule {field} {op} {value}: {result} (actual: {actual})")
            return result
        except Exception as e:
            logger.error(f"Error evaluating rule: {e}")
            return False
    
    def _get_nested_value(self, obj: Dict, path: str) -> Any:
        """Get nested value from dict using dot notation."""
        keys = path.split(".")
        value = obj
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
