async def _create_token_for_user(client, username: str = "alice") -> str:
    await client.post(
        "/auth/register",
        json={"username": username, "password": "password123"},
    )
    login_response = await client.post(
        "/auth/login",
        json={"username": username, "password": "password123"},
    )
    return login_response.json()["access_token"]


async def test_create_user(client):
    response = await client.post(
        "/users/",
        json={"username": "alice", "password": "password123"},
    )

    assert response.status_code == 201
    assert response.json()["username"] == "alice"
    assert "hashed_password" not in response.json()


async def test_list_users_requires_auth(client):
    response = await client.get("/users/")

    assert response.status_code == 401


async def test_list_users(client):
    token = await _create_token_for_user(client)

    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert [user["username"] for user in response.json()] == ["alice"]


async def test_get_user(client):
    token = await _create_token_for_user(client)

    response = await client.get(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


async def test_update_user(client):
    token = await _create_token_for_user(client)

    response = await client.patch(
        "/users/1",
        json={"username": "renamed"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "renamed"


async def test_delete_user(client):
    token = await _create_token_for_user(client)

    response = await client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"

    response = await client.get(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
