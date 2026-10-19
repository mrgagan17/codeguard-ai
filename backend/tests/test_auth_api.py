import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login_user():
    import uuid
    uid = str(uuid.uuid4())[:8]
    username = f"user_{uid}"
    email = f"{username}@example.com"
    password = "TestPassword123!"

    # Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
        "full_name": "Test User"
    })
    assert reg_res.status_code == 201

    # Login successfully
    login_res = client.post("/api/auth/login", json={
        "username_or_email": username,
        "password": password
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["user"]["username"] == username
    assert data["user"]["email"] == email

    # Login with wrong password
    bad_res = client.post("/api/auth/login", json={
        "username_or_email": username,
        "password": "wrongpassword"
    })
    assert bad_res.status_code == 401

def test_register_new_user_and_me():
    import uuid
    uid = str(uuid.uuid4())[:8]
    res = client.post("/api/auth/register", json={
        "email": f"user_{uid}@test.com",
        "username": f"user_{uid}",
        "password": "SecretPassword123!",
        "full_name": "Test User"
    })
    assert res.status_code == 201
    data = res.json()
    token = data["access_token"]
    assert token

    # Test /me with token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == f"user_{uid}"
    assert me_data["email"] == f"user_{uid}@test.com"
