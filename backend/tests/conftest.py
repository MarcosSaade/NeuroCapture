import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

# tests/conftest.py
import asyncio
import uuid # Import the uuid module
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.api.dependencies import get_db

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for session-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Create all tables before tests, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Provide a clean database session for each test."""
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
def client(db_session):
    """Provide an AsyncClient with an ASGI transport against the FastAPI app."""
    # Override get_db dependency to use our SQLite session
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client

    # Teardown
    asyncio.get_event_loop().run_until_complete(client.aclose())
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_patient(client: AsyncClient):
    """Create a new patient for testing and yield its data."""
    patient_data = {
        "study_identifier": f"TestPatient-{uuid.uuid4()}" # Generate unique study_identifier
    }
    response = await client.post("/api/v1/patients/", json=patient_data)
    assert response.status_code == 201, f"Failed to create patient: {response.text}"
    patient_json = response.json()
    yield patient_json
