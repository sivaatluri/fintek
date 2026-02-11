"""Tests for workflow state machine."""
import pytest
from engine.state_machine import WorkflowStateMachine
from models import WorkflowExecutionStatus


def test_valid_transitions():
    """Test valid state transitions."""
    machine = WorkflowStateMachine(None)
    
    assert machine.can_transition(
        WorkflowExecutionStatus.RECEIVED,
        WorkflowExecutionStatus.MATCHED,
    )
    
    assert machine.can_transition(
        WorkflowExecutionStatus.MATCHED,
        WorkflowExecutionStatus.RUNNING,
    )
    
    assert machine.can_transition(
        WorkflowExecutionStatus.RUNNING,
        WorkflowExecutionStatus.SUCCEEDED,
    )


def test_invalid_transitions():
    """Test invalid state transitions."""
    machine = WorkflowStateMachine(None)
    
    # Cannot go from RECEIVED to RUNNING
    assert not machine.can_transition(
        WorkflowExecutionStatus.RECEIVED,
        WorkflowExecutionStatus.RUNNING,
    )
    
    # Cannot go from SUCCEEDED to anything
    assert not machine.can_transition(
        WorkflowExecutionStatus.SUCCEEDED,
        WorkflowExecutionStatus.RUNNING,
    )


def test_retry_transitions():
    """Test retry state transitions."""
    machine = WorkflowStateMachine(None)
    
    # Can retry from FAILED
    assert machine.can_transition(
        WorkflowExecutionStatus.FAILED,
        WorkflowExecutionStatus.RETRYING,
    )
    
    # Can run from RETRYING
    assert machine.can_transition(
        WorkflowExecutionStatus.RETRYING,
        WorkflowExecutionStatus.RUNNING,
    )
