import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _require_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def make_async_database_url(url: str) -> str:
    """Normalize common sync SQLAlchemy URLs to async drivers."""
    replacements = {
        "mysql+pymysql://": "mysql+aiomysql://",
        "mysql://": "mysql+aiomysql://",
        "postgresql+psycopg2://": "postgresql+asyncpg://",
        "postgresql://": "postgresql+asyncpg://",
        "sqlite:///": "sqlite+aiosqlite:///",
    }
    for source, target in replacements.items():
        if url.startswith(source):
            return url.replace(source, target, 1)
    return url


SQLALCHEMY_DATABASE_URL = _require_database_url()
ASYNC_DATABASE_URL = make_async_database_url(SQLALCHEMY_DATABASE_URL)

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
