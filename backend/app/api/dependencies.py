from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an AsyncSession for each request, 
    and ensures it’s closed afterwards.
    """
    async with async_session() as session:
        yield session