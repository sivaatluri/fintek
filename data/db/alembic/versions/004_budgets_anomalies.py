"""Budgets and anomalies tables

Revision ID: 004
Revises: 003
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create budgets and anomalies tables."""
    
    # ==========================================================================
    # BUDGETS
    # ==========================================================================
    op.create_table(
        'budgets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('period', sa.Enum('monthly', 'quarterly', 'yearly', 'custom', name='budgetperiod'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('threshold_warning', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('threshold_critical', sa.Integer(), nullable=False, server_default='95'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('alert_emails', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_budget_org', 'budgets', ['org_id'])
    op.create_index('idx_budget_tenant', 'budgets', ['tenant_id'])
    op.create_index('idx_budget_period', 'budgets', ['period'])
    op.create_index('idx_budget_dates', 'budgets', ['start_date', 'end_date'])
    op.create_index('idx_budget_active', 'budgets', ['is_active'])
    op.create_index('idx_budget_org_active', 'budgets', ['org_id', 'is_active'])
    
    # ==========================================================================
    # ANOMALIES
    # ==========================================================================
    op.create_table(
        'anomalies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=True),
        sa.Column('cloud_account_id', sa.String(36), nullable=True),
        sa.Column('anomaly_type', sa.Enum('spike', 'drop', 'trend', 'unusual_pattern', name='anomalytype'), nullable=False),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='anomalyseverity'), nullable=False),
        sa.Column('status', sa.Enum('open', 'investigating', 'resolved', 'false_positive', name='anomalystatus'), 
                  nullable=False, server_default='open'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('expected_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('actual_cost', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('deviation_percent', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('affected_resources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cloud_account_id'], ['cloud_accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_anomaly_org', 'anomalies', ['org_id'])
    op.create_index('idx_anomaly_tenant', 'anomalies', ['tenant_id'])
    op.create_index('idx_anomaly_account', 'anomalies', ['cloud_account_id'])
    op.create_index('idx_anomaly_type', 'anomalies', ['anomaly_type'])
    op.create_index('idx_anomaly_severity', 'anomalies', ['severity'])
    op.create_index('idx_anomaly_status', 'anomalies', ['status'])
    op.create_index('idx_anomaly_detected', 'anomalies', ['detected_at'])
    op.create_index('idx_anomaly_org_status', 'anomalies', ['org_id', 'status'])
    op.create_index('idx_anomaly_dates', 'anomalies', ['start_date', 'end_date'])


def downgrade() -> None:
    """Drop budgets and anomalies tables."""
    op.drop_table('anomalies')
    op.execute('DROP TYPE anomalystatus')
    op.execute('DROP TYPE anomalyseverity')
    op.execute('DROP TYPE anomalytype')
    
    op.drop_table('budgets')
    op.execute('DROP TYPE budgetperiod')
