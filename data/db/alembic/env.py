"""Alembic environment configuration for FinOps database migrations."""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all model bases
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import models - they will be registered with metadata
try:
    from services.auth_service.src.models.rbac import Base as AuthBase
    for table in AuthBase.metadata.tables.values():
        table.to_metadata(Base.metadata)
except ImportError:
    print("Warning: Could not import auth service models")

try:
    from services.tenant_service.src.models.models import Base as TenantBase
    for table in TenantBase.metadata.tables.values():
        table.to_metadata(Base.metadata)
except ImportError:
    print("Warning: Could not import tenant service models")

# Set target metadata for migrations
target_metadata = Base.metadata

# Allow DATABASE_URL environment variable to override config
database_url = os.getenv('DATABASE_URL')
if database_url:
    config.set_main_option('sqlalchemy.url', database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
