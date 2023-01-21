from __future__ import with_statement

import asyncio

from sqlalchemy import pool
from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

from logging.config import fileConfig
import logging

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
# pylint: disable=no-member
config = context.config

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

try:
    from fastapi_async_sqlalchemy import db

    async def get_app_sqlalchemy():
        async with db():
            config.set_main_option(
                'sqlalchemy.url',
                str(db.session.get_bind().engine.url).replace('%', '%%')
            )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_app_sqlalchemy())

except:
    # TODO: Add url to MigrationsConfig
    config.set_main_option(
        'sqlalchemy.url',
        'sqlite:///?check_same_thread=false'
    )


def get_metadata():
    import importlib
    metadata_package_name = config.get_main_option('metadata_package')
    metadata_class_name = config.get_main_option('metadata_class')
    if metadata_package_name and metadata_class_name:
        try:
            metadata_package = importlib.import_module(metadata_package_name)
            metadata_class = getattr(metadata_package, metadata_class_name)
            return metadata_class.metadata
        except Exception:
            logging.error('Failed to import module.', metadata_package_name)
            return None
    else:
        logging.info('Metadata package or class not provided.')
    return None


target_metadata = get_metadata()


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
