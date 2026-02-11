"""Database models for tenant service."""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CloudProvider(str, Enum):
    """Cloud provider enumeration."""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE = "oracle"
    AKAMAI = "akamai"
    DATACENTER = "datacenter"


class Organization(Base):
    """Organization model - top-level entity."""

    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100))
    
    # Settings
    settings = Column(JSON, default=dict)  # Org-specific settings
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(36))
    updated_by = Column(String(36))
    
    # Relationships
    tenants = relationship("Tenant", back_populates="organization", cascade="all, delete-orphan")
    cloud_accounts = relationship("CloudAccount", back_populates="organization", cascade="all, delete-orphan")
    views = relationship("PersonaView", back_populates="organization", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_org_name_active", "name", "is_active"),
    )


class Tenant(Base):
    """Tenant model - logical grouping within an organization."""

    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(36))
    updated_by = Column(String(36))
    
    # Relationships
    organization = relationship("Organization", back_populates="tenants")
    cloud_accounts = relationship("CloudAccount", back_populates="tenant")

    __table_args__ = (
        Index("idx_tenant_org_slug", "org_id", "slug", unique=True),
        Index("idx_tenant_org_active", "org_id", "is_active"),
    )


class CloudAccount(Base):
    """Cloud account model - represents cloud provider accounts."""

    __tablename__ = "cloud_accounts"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    
    name = Column(String(255), nullable=False)
    provider = Column(SQLEnum(CloudProvider), nullable=False, index=True)
    
    # Provider-specific identifiers
    account_id = Column(String(255), nullable=False, index=True)  # AWS Account ID, Azure Subscription ID, etc.
    account_name = Column(String(255))  # Human-readable name from provider
    
    # Configuration
    credentials = Column(JSON)  # Encrypted credentials or reference to secret store
    settings = Column(JSON, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_connected = Column(Boolean, default=False, nullable=False)  # Connection status
    last_sync_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(36))
    updated_by = Column(String(36))
    
    # Relationships
    organization = relationship("Organization", back_populates="cloud_accounts")
    tenant = relationship("Tenant", back_populates="cloud_accounts")

    __table_args__ = (
        Index("idx_cloud_account_org_provider", "org_id", "provider"),
        Index("idx_cloud_account_provider_id", "provider", "account_id"),
    )


class PersonaView(Base):
    """Persona view model - saved dashboards/filters for different personas."""

    __tablename__ = "persona_views"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Persona type (executive, finops, engineering, product_ops, etc.)
    persona = Column(String(50), nullable=False, index=True)
    
    # View configuration
    config = Column(JSON, nullable=False)  # Dashboard config, filters, widgets, etc.
    
    # Visibility
    is_default = Column(Boolean, default=False, nullable=False)  # Default view for persona
    is_shared = Column(Boolean, default=False, nullable=False)  # Shared across org
    owner_id = Column(String(36))  # User who owns this view
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(36))
    updated_by = Column(String(36))
    
    # Relationships
    organization = relationship("Organization", back_populates="views")

    __table_args__ = (
        Index("idx_view_org_persona", "org_id", "persona"),
        Index("idx_view_org_slug", "org_id", "slug", unique=True),
    )


class AuditLog(Base):
    """Audit log model - tracks all changes to entities."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # What was changed
    entity_type = Column(String(50), nullable=False, index=True)  # 'organization', 'tenant', etc.
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(20), nullable=False, index=True)  # 'create', 'update', 'delete'
    
    # Who changed it
    user_id = Column(String(36), index=True)
    org_id = Column(String(36), nullable=False, index=True)
    
    # What changed
    changes = Column(JSON)  # Old and new values
    
    # When
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(36), index=True)

    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_org_created", "org_id", "created_at"),
        Index("idx_audit_user_created", "user_id", "created_at"),
    )
