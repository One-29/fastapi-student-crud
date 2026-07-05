import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from database import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

@pytest.fixture(scope="session")
async def engine():
    url = os.getenv("TEST_DATABASE_URL")
    assert url is not None, "TEST_DATABASE_URL is not set"
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.create_all(c))

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.drop_all(c))

    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    # 每个测试开始前清空所有表，保证测试之间数据隔离
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    test_session = async_sessionmaker(engine, class_=AsyncSession)
    async with test_session() as session:
        yield session