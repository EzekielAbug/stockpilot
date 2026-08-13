"""Alembic migration env config

This file tells Alembic:
1. Where to find the database connection
2. Where to find models
3. How to run migration
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool 
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings
from app.models.base import Base

# all model imports

config = context.config

# py logging setup

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migration_offline() -> None:
    """Migrations in offline mode
    
    Generates sql scripts without connecting to the db
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    """Run migrations with a given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in online with async eng"""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migration_online() -> None:
    """Entry point for online migration"""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migration_offline()
else:
    run_migration_online()