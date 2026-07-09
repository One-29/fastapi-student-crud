async def test_register_login_me_and_refresh(client):
    register_response = await client.post(
        "/auth/register",
        json={"username": "alice", "password": "password123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["username"] == "alice"
    assert "hashed_password" not in register_response.json()

    login_response = await client.post(
        "/auth/login",
        json={"username": "alice", "password": "password123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "alice"

    refresh_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]


async def test_register_duplicate_username(client):
    payload = {"username": "bob", "password": "password123"}
    first_response = await client.post("/auth/register", json=payload)
    second_response = await client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username already registered"


async def test_login_rejects_bad_password(client):
    await client.post(
        "/auth/register",
        json={"username": "carol", "password": "password123"},
    )

    response = await client.post(
        "/auth/login",
        json={"username": "carol", "password": "wrong-password"},
    )

    assert response.status_code == 401
