import os
import sys
import pytest
import httpx
from main import app
from database import get_db
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

    # 异步多线程环境， 不需要检查线程一致性
    connect_args = {}
    if "sqlite" in url:
        connect_args["check_same_thread"] = False
    engine = create_async_engine(url, connect_args=connect_args)

    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.create_all(c))

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.drop_all(c))

    await engine.dispose()


@pytest.fixture
async def db_session(engine):

    connection = await engine.connect()
    trans = await connection.begin()

    test_session = async_sessionmaker(
        bind=connection,  # ← 关键：绑到手动开的连接
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with test_session() as session:
        yield session

    await trans.rollback()
    await trans.connection.close()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()