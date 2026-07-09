from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


async def get_users(db: AsyncSession) -> List[User]:
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str, hashed_password: str) -> User:
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(new_user)
    return new_user


async def update_user(
    db: AsyncSession,
    user: User,
    *,
    username: Optional[str] = None,
    hashed_password: Optional[str] = None,
) -> User:
    if username is not None:
        user.username = username
    if hashed_password is not None:
        user.hashed_password = hashed_password

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> User:
    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return user
