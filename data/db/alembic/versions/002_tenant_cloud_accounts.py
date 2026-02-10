"""Tenant and cloud account tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tenant and cloud account tables."""
    
    # ==========================================================================
    # TENANTS
    # ==========================================================================
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_tenant_org', 'tenants', ['org_id'])
    op.create_index('idx_tenant_name', 'tenants', ['name'])
    op.create_index('idx_tenant_org_slug', 'tenants', ['org_id', 'slug'], unique=True)
    op.create_index('idx_tenant_org_active', 'tenants', ['org_id', 'is_active'])
    op.create_index('idx_tenant_created_at', 'tenants', ['created_at'])
    
    # ==========================================================================
    # CLOUD_ACCOUNTS
    # ==========================================================================
    op.create_table(
        'cloud_accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('org_id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('provider', sa.Enum('aws', 'azure', 'gcp', 'oracle', 'akamai', 'datacenter', name='cloudprovider'), nullable=False),
        sa.Column('account_id', sa.String(255), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=True),
        sa.Column('credentials', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_connected', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_cloud_account_org', 'cloud_accounts', ['org_id'])
    op.create_index('idx_cloud_account_tenant', 'cloud_accounts', ['tenant_id'])
    op.create_index('idx_cloud_account_provider', 'cloud_accounts', ['provider'])
    op.create_index('idx_cloud_account_org_provider', 'cloud_accounts', ['org_id', 'provider'])
    op.create_index('idx_cloud_account_provider_id', 'cloud_accounts', ['provider', 'account_id'])
    op.create_index('idx_cloud_account_created_at', 'cloud_accounts', ['created_at'])


def downgrade() -> None:
    """Drop tenant and cloud account tables."""
    op.drop_table('cloud_accounts')
    op.drop_table('tenants')
    op.execute('DROP TYPE cloudprovider')
