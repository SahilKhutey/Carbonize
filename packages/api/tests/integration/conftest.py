"""
Shared configuration and database setup for integration tests.
"""

import pytest
import cbms_api.database.connection as conn_mod
import database.connection as conn_mod_alt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

# Initialize a shared SQLite in-memory engine using StaticPool to ensure connection is kept alive
# and connect_args to allow thread-safe access from the FastAPI testing client.
sqlite_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
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
