import pytest
import cbms_api.database.connection as conn_mod
import database.connection as conn_mod_alt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

# Initialize a shared SQLite file-based engine to prevent ASGI transport deadlocks under concurrent load
sqlite_test_engine = create_async_engine(
    "sqlite+aiosqlite:///test_test.db",
    connect_args={"check_same_thread": False},
    pool_size=100,
    max_overflow=100,
)

sqlite_sessionmaker = async_sessionmaker(
    bind=sqlite_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Apply monkeypatching globally to connection modules
conn_mod.engine = sqlite_test_engine
conn_mod.async_session_maker = sqlite_sessionmaker
conn_mod_alt.engine = sqlite_test_engine
conn_mod_alt.async_session_maker = sqlite_sessionmaker
