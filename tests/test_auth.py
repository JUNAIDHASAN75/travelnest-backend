def test_register_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jane Traveler",
            "email": "jane@example.com",
            "password": "StrongPassword123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Traveler"
    assert data["role"] == "user"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "StrongPassword123!"
        }
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "AnotherPassword456!"
        }
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_login_success_and_me(client):
    # Register
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecretPassword123!"
        }
    )

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "john@example.com",
            "password": "SecretPassword123!"
        }
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Access /me
    access_token = token_data["access_token"]
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "john@example.com"


def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Wrong Pass User",
            "email": "wrongpass@example.com",
            "password": "CorrectPassword123!"
        }
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "InvalidPassword!"
        }
    )
    assert login_res.status_code == 401


def test_unauthorized_request(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_refresh_token_and_logout(client):
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Refresh Tester",
            "email": "refresh@example.com",
            "password": "Password789!"
        }
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "Password789!"
        }
    )
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    # Refresh
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert new_tokens["refresh_token"] != refresh_token

    # Old refresh token should be revoked (rotation)
    old_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert old_res.status_code == 401

    # Logout with new refresh token
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert logout_res.status_code == 200

    # Using revoked token should fail
    after_logout_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert after_logout_res.status_code == 401
