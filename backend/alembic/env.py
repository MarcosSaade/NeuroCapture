import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# —————— Load environment ——————
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# —————— Alembic Config ——————
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# —————— Target metadata for 'autogenerate' ——————
# Adjust the import path to wherever your Base lives
from app.models import Base  
target_metadata = Base.metadata

# —————— Helper: get URL from env or fallback ——————
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://marcos:password@localhost:5432/neurocapture"
)

# —————— OFFLINE (no DB connection) ——————
def run_migrations_offline() -> None:
    url = DB_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# —————— ONLINE (with DB) ——————
def run_migrations_online() -> None:
    # 1. Create a **sync** engine for autogenerate
    sync_url = DB_URL.replace("asyncpg", "psycopg2")
    sync_engine = create_engine(sync_url, poolclass=pool.NullPool)

    with sync_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,   # detect type changes
        )
        with context.begin_transaction():
            context.run_migrations()

# —————— Entrypoint ——————
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
