import asyncio

from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import create_database, drop_database, database_exists

from tgbot.models.base import Base
from config import settings


database_settings = settings.DATABASES['default']


@pytest.fixture(scope='session')
def engine():
    # DATABASE_TEST_URL = f"postgresql+asyncpg://test_user:test_password@localhost:5433/test_db_postgre"
    DATABASE_TEST_URL = f"postgresql+asyncpg://{database_settings['USER']}:{database_settings['PASSWORD']}" \
                        f"@{database_settings['HOST']}:{database_settings['PORT']}/{database_settings['NAME']}"
    engine_test = create_async_engine(DATABASE_TEST_URL, poolclass=NullPool)
    # session_maker = async_sessionmaker(bind=engine_test, expire_on_commit=False)
    yield engine_test
    engine_test.sync_engine.dispose()


@pytest.fixture()
async def deploy_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def session(engine, deploy_database):
    async with AsyncSession(engine) as session:
        yield session

