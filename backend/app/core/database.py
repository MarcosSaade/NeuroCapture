import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()  # loads DATABASE_URL into env

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var not set")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the async session factory
async_session: async_sessionmaker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
