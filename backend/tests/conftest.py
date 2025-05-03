import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.api.dependencies import get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine & session factory
engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 1. Allow session-scoped event loop for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 2. Prepare and teardown the test database
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 3. Provide a database session for each test
@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

# 4. Provide a real AsyncClient (non‐async fixture), with dependency override
@pytest.fixture
def client(db_session):
    # override get_db dependency
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    client = AsyncClient(app=app, base_url="http://test")
    yield client

    # teardown: clear override and close client
    app.dependency_overrides.clear()
    asyncio.get_event_loop().run_until_complete(client.aclose())
