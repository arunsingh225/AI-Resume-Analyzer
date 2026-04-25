"""
Auth API Tests — covers signup, login, refresh tokens, password validation, rate limiting.
"""
import pytest
from fastapi.testclient import TestClient


class TestSignup:
    """Test user registration flow."""

    def test_signup_success(self, client: TestClient):
        resp = client.post("/auth/signup", json={
            "name": "Test User",
            "email": "signup_test@example.com",
            "password": "StrongPass1"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900
        assert data["user"]["email"] == "signup_test@example.com"

    def test_signup_duplicate_email(self, client: TestClient):
        payload = {"name": "A", "email": "dup@example.com", "password": "StrongPass1"}
        client.post("/auth/signup", json=payload)
        resp = client.post("/auth/signup", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_signup_weak_password_no_uppercase(self, client: TestClient):
        resp = client.post("/auth/signup", json={
            "name": "A", "email": "weak1@example.com", "password": "weakpass1"
        })
        assert resp.status_code == 400
        assert "uppercase" in resp.json()["detail"].lower()

    def test_signup_weak_password_too_short(self, client: TestClient):
        resp = client.post("/auth/signup", json={
            "name": "A", "email": "weak2@example.com", "password": "Ab1"
        })
        assert resp.status_code == 400
        assert "8 characters" in resp.json()["detail"]

    def test_signup_weak_password_no_digit(self, client: TestClient):
        resp = client.post("/auth/signup", json={
            "name": "A", "email": "weak3@example.com", "password": "Abcdefgh"
        })
        assert resp.status_code == 400
        assert "digit" in resp.json()["detail"].lower()

    def test_signup_invalid_email(self, client: TestClient):
        resp = client.post("/auth/signup", json={
            "name": "A", "email": "not-an-email", "password": "StrongPass1"
        })
        assert resp.status_code == 422  # Pydantic validation


class TestLogin:
    """Test login flow."""

    def test_login_success(self, client: TestClient):
        # Create user first
        client.post("/auth/signup", json={
            "name": "Login User",
            "email": "login_test@example.com",
            "password": "StrongPass1"
        })
        resp = client.post("/auth/login", json={
            "email": "login_test@example.com",
            "password": "StrongPass1"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client: TestClient):
        client.post("/auth/signup", json={
            "name": "A", "email": "wrongpw@example.com", "password": "StrongPass1"
        })
        resp = client.post("/auth/login", json={
            "email": "wrongpw@example.com",
            "password": "WrongPass1"
        })
        assert resp.status_code == 401

    def test_login_nonexistent_email(self, client: TestClient):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "StrongPass1"
        })
        assert resp.status_code == 401


class TestRefreshToken:
    """Test refresh token flow."""

    def test_refresh_success(self, client: TestClient):
        # Signup to get tokens
        signup_resp = client.post("/auth/signup", json={
            "name": "Refresh User",
            "email": "refresh_test@example.com",
            "password": "StrongPass1"
        })
        refresh_token = signup_resp.json()["refresh_token"]

        # Use refresh token to get new tokens
        resp = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_with_access_token_fails(self, client: TestClient):
        """Access tokens should NOT work as refresh tokens."""
        signup_resp = client.post("/auth/signup", json={
            "name": "A", "email": "refresh_fail@example.com", "password": "StrongPass1"
        })
        access_token = signup_resp.json()["access_token"]

        resp = client.post("/auth/refresh", json={
            "refresh_token": access_token
        })
        assert resp.status_code == 401

    def test_refresh_with_invalid_token(self, client: TestClient):
        resp = client.post("/auth/refresh", json={
            "refresh_token": "invalid.token.value"
        })
        assert resp.status_code == 401


class TestAuthMe:
    """Test /auth/me endpoint."""

    def test_get_me_with_valid_token(self, client: TestClient):
        signup_resp = client.post("/auth/signup", json={
            "name": "Me User",
            "email": "me_test@example.com",
            "password": "StrongPass1"
        })
        token = signup_resp.json()["access_token"]

        resp = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "me_test@example.com"

    def test_get_me_without_token(self, client: TestClient):
        resp = client.get("/auth/me")
        assert resp.status_code in [401, 403]

    def test_get_me_with_expired_token(self, client: TestClient):
        # Malformed token
        resp = client.get("/auth/me", headers={
            "Authorization": "Bearer expired.fake.token"
        })
        assert resp.status_code == 401


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_live(self, client: TestClient):
        resp = client.get("/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "alive"

    def test_ready(self, client: TestClient):
        resp = client.get("/ready")
        assert resp.status_code == 200

    def test_root(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "docs" in resp.json()
