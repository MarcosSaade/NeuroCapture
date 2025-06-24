"""
Database Configuration and Connection Management

Configures async SQLAlchemy engine and session factory for PostgreSQL database.
Handles environment variable loading and connection settings for the NeuroCapture API.

Features:
- Async database operations with asyncpg driver
- Environment-based configuration
- Connection pooling and session management
- Development-friendly query logging

Author: NeuroCapture Development Team
"""

import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    AsyncSession
)

# Load environment variables from .env file
load_dotenv()

# Database connection configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://neuro:capture@localhost:5432/neurocapture"
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable not set. "
        "Please configure database connection in .env file."
    )

# Create async engine with optimized settings
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",  # Log SQL queries in debug mode
    pool_size=20,          # Connection pool size
    max_overflow=30,       # Maximum overflow connections
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600,     # Recycle connections every hour
)

# Create async session factory
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects usable after commit
    autoflush=True,          # Auto-flush changes before queries
    autocommit=False,        # Manual transaction control
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide database sessions to FastAPI endpoints.
    
    Yields:
        AsyncSession: Database session for the request
        
    Note:
        Automatically handles session cleanup and error rollback.
        Use as a FastAPI dependency: db: AsyncSession = Depends(get_db)
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
