import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

# Platform database lives next to the backend folder
_db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_db_path = os.path.join(_db_dir, "platform.db")

ASYNC_DB_URL = f"sqlite+aiosqlite:///{_db_path}"
SYNC_DB_URL = f"sqlite:///{_db_path}"

# Async engine for FastAPI
async_engine = create_async_engine(ASYNC_DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync engine for background tasks and seeding
sync_engine = create_engine(SYNC_DB_URL, echo=False)
SyncSessionLocal = sessionmaker(bind=sync_engine)


# Enable WAL mode and foreign keys for SQLite
@event.listens_for(sync_engine, "connect")
def _set_sqlite_pragma_sync(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
