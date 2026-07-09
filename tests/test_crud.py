import pytest

from crud import create_user, delete_user, get_user_by_id, get_user_by_username, get_users, update_user


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = await create_user(db_session, "alice", "hashed-password")

    assert user.id is not None
    assert user.username == "alice"
    assert user.hashed_password == "hashed-password"


@pytest.mark.asyncio
async def test_get_user_by_id(db_session):
    created = await create_user(db_session, "bob", "hashed-password")

    fetched = await get_user_by_id(db_session, created.id)

    assert fetched is not None
    assert fetched.username == "bob"


@pytest.mark.asyncio
async def test_get_user_by_username(db_session):
    await create_user(db_session, "carol", "hashed-password")

    fetched = await get_user_by_username(db_session, "carol")

    assert fetched is not None
    assert fetched.username == "carol"


@pytest.mark.asyncio
async def test_get_users(db_session):
    await create_user(db_session, "dave", "hashed-password")
    await create_user(db_session, "erin", "hashed-password")

    users = await get_users(db_session)

    assert [user.username for user in users] == ["dave", "erin"]


@pytest.mark.asyncio
async def test_update_user(db_session):
    created = await create_user(db_session, "oldname", "old-hash")

    updated = await update_user(
        db_session,
        created,
        username="newname",
        hashed_password="new-hash",
    )

    assert updated.username == "newname"
    assert updated.hashed_password == "new-hash"


@pytest.mark.asyncio
async def test_delete_user(db_session):
    created = await create_user(db_session, "delete-me", "hashed-password")

    deleted = await delete_user(db_session, created)
    fetched = await get_user_by_id(db_session, deleted.id)

    assert deleted.username == "delete-me"
    assert fetched is None
