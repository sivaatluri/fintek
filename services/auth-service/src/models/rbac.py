"""Database models for RBAC."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association tables for many-to-many relationships
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
    Column("org_id", String(36), nullable=False, index=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    
    # External ID (from OIDC/SAML)
    external_id = Column(String(255), unique=True, index=True)
    external_provider = Column(String(50))  # 'oidc', 'saml', 'local'
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    """Role model."""

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255))
    description = Column(Text)
    
    # Hierarchy
    is_system = Column(Boolean, default=False, nullable=False)  # System vs custom role
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Permission model."""

    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # e.g., 'costs:read'
    display_name = Column(String(255))
    description = Column(Text)
    resource = Column(String(100), nullable=False, index=True)  # e.g., 'costs'
    action = Column(String(50), nullable=False)  # e.g., 'read', 'write'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class UserOrganization(Base):
    """User-Organization association with role."""

    __tablename__ = "user_organizations"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    org_id = Column(String(36), nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Session(Base):
    """User session model."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Session metadata
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    
    # OIDC/SAML session data
    id_token = Column(Text)  # Store encrypted
    refresh_token = Column(Text)  # Store encrypted
    saml_session_index = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
