import pytest

from tests.conftest import auth_headers

pytestmark = pytest.mark.asyncio


async def test_signup_creates_student(client):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"name": "Aishwary", "email": "aishwary@test.com", "password": "SecurePass1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "aishwary@test.com"
    assert body["role"] == "student"
    assert "password" not in body
    assert "password_hash" not in body


async def test_signup_duplicate_email_rejected(client):
    payload = {"name": "Test User", "email": "dup@test.com", "password": "SecurePass1"}
    r1 = await client.post("/api/v1/auth/signup", json=payload)
    r2 = await client.post("/api/v1/auth/signup", json=payload)
    assert r1.status_code == 201
    assert r2.status_code == 409


async def test_login_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/signup", json={"name": "Test User", "email": "wrongpw@test.com", "password": "SecurePass1"}
    )
    resp = await client.post("/api/v1/auth/login", json={"email": "wrongpw@test.com", "password": "nope"})
    assert resp.status_code == 401


async def test_login_returns_token_pair(client):
    await client.post("/api/v1/auth/signup", json={"name": "Test User", "email": "tok@test.com", "password": "SecurePass1"})
    resp = await client.post("/api/v1/auth/login", json={"email": "tok@test.com", "password": "SecurePass1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_get_profile_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_get_profile_with_valid_token(client, student_tokens):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers(student_tokens))
    assert resp.status_code == 200
    assert resp.json()["role"] == "student"


async def test_refresh_token_rotation(client, student_tokens):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": student_tokens["refresh_token"]})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert new_tokens["access_token"] != student_tokens["access_token"]

    # Old refresh token should now be blacklisted (rotation)
    reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": student_tokens["refresh_token"]})
    assert reuse_resp.status_code == 401


async def test_logout_revokes_refresh_token(client, student_tokens):
    logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": student_tokens["refresh_token"]})
    assert logout_resp.status_code == 200

    reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": student_tokens["refresh_token"]})
    assert reuse_resp.status_code == 401


async def test_change_password(client, student_tokens):
    resp = await client.post(
        "/api/v1/auth/me/change-password",
        headers=auth_headers(student_tokens),
        json={"current_password": "TestPass123", "new_password": "NewSecurePass1"},
    )
    assert resp.status_code == 200
