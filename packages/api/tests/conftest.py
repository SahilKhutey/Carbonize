import pytest
import cbms_api.database.connection as conn_mod
import database.connection as conn_mod_alt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

import sqlite3
import datetime

# Register explicit sqlite3 adapters and converters for Python 3.12+ compatibility
sqlite3.register_adapter(datetime.date, lambda val: val.isoformat())
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
sqlite3.register_converter("date", lambda val: datetime.date.fromisoformat(val.decode()))
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode()))
sqlite3.register_converter("datetime", lambda val: datetime.datetime.fromisoformat(val.decode()))

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
