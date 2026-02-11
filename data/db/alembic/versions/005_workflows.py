"""Workflow tables

Revision ID: 005
Revises: 004
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workflow definition, execution, and step tables."""
    
    # ==========================================================================
    # WORKFLOW_DEFINITIONS
    # ==========================================================================
    op.create_table(
        'workflow_definitions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger_type', sa.Enum('event', 'schedule', 'manual', name='workflowtrigger'), nullable=False),
        sa.Column('trigger_config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('conditions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('actions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_template', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_workflow_def_org', 'workflow_definitions', ['org_id'])
    op.create_index('idx_workflow_def_trigger', 'workflow_definitions', ['trigger_type'])
    op.create_index('idx_workflow_def_active', 'workflow_definitions', ['is_active'])
    op.create_index('idx_workflow_def_org_active', 'workflow_definitions', ['org_id', 'is_active'])
    
    # ==========================================================================
    # WORKFLOW_EXECUTIONS
    # ==========================================================================
    op.create_table(
        'workflow_executions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_definition_id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='workflowstatus'), 
                  nullable=False, server_default='pending'),
        sa.Column('trigger_event', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('trigger_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('triggered_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['workflow_definition_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_workflow_exec_def', 'workflow_executions', ['workflow_definition_id'])
    op.create_index('idx_workflow_exec_org', 'workflow_executions', ['org_id'])
    op.create_index('idx_workflow_exec_status', 'workflow_executions', ['status'])
    op.create_index('idx_workflow_exec_created', 'workflow_executions', ['created_at'])
    op.create_index('idx_workflow_exec_org_status', 'workflow_executions', ['org_id', 'status'])
    
    # ==========================================================================
    # WORKFLOW_STEPS
    # ==========================================================================
    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_execution_id', sa.String(36), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=False),
        sa.Column('step_type', sa.String(50), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'skipped', name='stepstatus'), 
                  nullable=False, server_default='pending'),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('retries', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workflow_execution_id'], ['workflow_executions.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_workflow_step_exec', 'workflow_steps', ['workflow_execution_id'])
    op.create_index('idx_workflow_step_status', 'workflow_steps', ['status'])
    op.create_index('idx_workflow_step_order', 'workflow_steps', ['workflow_execution_id', 'step_order'])
    
    # ==========================================================================
    # WORKFLOW_EXTERNAL_REFS - Links to external systems (Jira, ServiceNow, etc.)
    # ==========================================================================
    op.create_table(
        'workflow_external_refs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_execution_id', sa.String(36), nullable=False),
        sa.Column('workflow_step_id', sa.String(36), nullable=True),
        sa.Column('external_system', sa.String(50), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('external_url', sa.String(1000), nullable=True),
        sa.Column('external_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workflow_execution_id'], ['workflow_executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_step_id'], ['workflow_steps.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_workflow_extref_exec', 'workflow_external_refs', ['workflow_execution_id'])
    op.create_index('idx_workflow_extref_step', 'workflow_external_refs', ['workflow_step_id'])
    op.create_index('idx_workflow_extref_system', 'workflow_external_refs', ['external_system'])
    op.create_index('idx_workflow_extref_external_id', 'workflow_external_refs', ['external_system', 'external_id'])


def downgrade() -> None:
    """Drop workflow tables."""
    op.drop_table('workflow_external_refs')
    
    op.drop_table('workflow_steps')
    op.execute('DROP TYPE stepstatus')
    
    op.drop_table('workflow_executions')
    op.execute('DROP TYPE workflowstatus')
    
    op.drop_table('workflow_definitions')
    op.execute('DROP TYPE workflowtrigger')
