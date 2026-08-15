import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.main import app
from app.database import get_db
from app.config import settings

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def db_session():
    """Provides a database session that rolls back after every test."""
    test_engine = create_async_engine(settings.DATABASE_URL)
    
    async with test_engine.connect() as conn:
        transaction = await conn.begin()
        await conn.begin_nested()
        
        async_session = AsyncSession(conn, expire_on_commit=False)
        yield async_session
        await async_session.close()
        await transaction.rollback()
        
    await test_engine.dispose()

@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
        
    app.dependency_overrides.clear()