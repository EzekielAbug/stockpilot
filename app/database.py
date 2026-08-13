"""Database connection and session management.

This module creates the async database engine and provides
session factories for use throughout the application.

Key concepts: 
    - Engine: The connection to the database (like a phone line)
    - Session: A conversation over that connection (like a phone call)
    - Session Factory: Creates new session on demand
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# db engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# session factory 
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,

)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a database session for each request.
    
    This is a FastAPI dependency. It's:
    1. Creates a new session
    2. Gives it to the endpoint function
    3. Closes it when the request is done. 

    Usage in an endpoint:
        @app.get("/products")
        async def list_products(db: AsyncSession = Depends(get_db)):
        ...

    Yields: 
        An async SQLAlchemy session.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise