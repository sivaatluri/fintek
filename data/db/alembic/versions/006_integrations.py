"""Integration and delivery tables

Revision ID: 006
Revises: 005
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create integration and integration_delivery tables."""
    
    # ==========================================================================
    # INTEGRATIONS - Configuration for external integrations
    # ==========================================================================
    op.create_table(
        'integrations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('integration_type', sa.Enum(
            'jira', 'servicenow', 'zendesk', 'slack', 'teams', 
            'pagerduty', 'email', 'webhook', 'custom', 
            name='integrationtype'
        ), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('credentials', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_integration_org', 'integrations', ['org_id'])
    op.create_index('idx_integration_type', 'integrations', ['integration_type'])
    op.create_index('idx_integration_active', 'integrations', ['is_active'])
    op.create_index('idx_integration_org_type', 'integrations', ['org_id', 'integration_type'])
    
    # ==========================================================================
    # INTEGRATION_DELIVERIES - Track individual delivery attempts
    # ==========================================================================
    op.create_table(
        'integration_deliveries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('integration_id', sa.String(36), nullable=False),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('workflow_execution_id', sa.String(36), nullable=True),
        sa.Column('workflow_step_id', sa.String(36), nullable=True),
        sa.Column('status', sa.Enum('pending', 'sent', 'delivered', 'failed', 'retrying', name='deliverystatus'), 
                  nullable=False, server_default='pending'),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('response', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('external_url', sa.String(1000), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_execution_id'], ['workflow_executions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workflow_step_id'], ['workflow_steps.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_integration_delivery_integration', 'integration_deliveries', ['integration_id'])
    op.create_index('idx_integration_delivery_org', 'integration_deliveries', ['org_id'])
    op.create_index('idx_integration_delivery_workflow', 'integration_deliveries', ['workflow_execution_id'])
    op.create_index('idx_integration_delivery_step', 'integration_deliveries', ['workflow_step_id'])
    op.create_index('idx_integration_delivery_status', 'integration_deliveries', ['status'])
    op.create_index('idx_integration_delivery_created', 'integration_deliveries', ['created_at'])
    op.create_index('idx_integration_delivery_retry', 'integration_deliveries', ['status', 'next_retry_at'])
    op.create_index('idx_integration_delivery_external', 'integration_deliveries', ['integration_id', 'external_id'])


def downgrade() -> None:
    """Drop integration and delivery tables."""
    op.drop_table('integration_deliveries')
    op.execute('DROP TYPE deliverystatus')
    
    op.drop_table('integrations')
    op.execute('DROP TYPE integrationtype')
