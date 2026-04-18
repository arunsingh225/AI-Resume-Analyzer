"""
Integration tests for API endpoints.
"""
import pytest


class TestHealthEndpoints:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "status" in r.json()

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


class TestAuthAPI:
    def test_signup_success(self, client):
        import uuid
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        r = client.post("/auth/signup", json={
            "name": "New User",
            "email": email,
            "password": "SecurePass123"
        })
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert "user" in data

    def test_signup_duplicate_email(self, client):
        import uuid
        email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
        client.post("/auth/signup", json={
            "name": "First", "email": email, "password": "FirstPass1"
        })
        r = client.post("/auth/signup", json={
            "name": "Second", "email": email, "password": "SecondPass2"
        })
        assert r.status_code == 400

    def test_signup_weak_password_rejected(self, client):
        """Verify that the password validator rejects weak passwords."""
        import uuid
        email = f"weak_{uuid.uuid4().hex[:8]}@example.com"
        r = client.post("/auth/signup", json={
            "name": "Weak PW", "email": email, "password": "short"
        })
        assert r.status_code == 400
        assert "Password must contain" in r.json()["detail"]

    def test_login_success(self, client):
        import uuid
        email = f"login_{uuid.uuid4().hex[:8]}@example.com"
        client.post("/auth/signup", json={
            "name": "Login User", "email": email, "password": "CorrectPass1"
        })
        r = client.post("/auth/login", json={
            "email": email, "password": "CorrectPass1"
        })
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_wrong_password(self, client):
        import uuid
        email = f"wp_{uuid.uuid4().hex[:8]}@example.com"
        client.post("/auth/signup", json={
            "name": "WP User", "email": email, "password": "CorrectPass1"
        })
        r = client.post("/auth/login", json={
            "email": email, "password": "WrongPass999"
        })
        assert r.status_code == 401

    def test_me_endpoint(self, client, auth_headers):
        r = client.get("/auth/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "email" in data

    def test_me_without_auth(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401


class TestResumeAnalyzeAPI:
    def test_rejects_non_pdf(self, client, auth_headers):
        r = client.post(
            "/api/resume/analyze",
            files={"file": ("test.txt", b"hello world" * 10, "text/plain")},
            headers=auth_headers
        )
        assert r.status_code == 400

    def test_rejects_empty_file(self, client, auth_headers):
        r = client.post(
            "/api/resume/analyze",
            files={"file": ("test.pdf", b"", "application/pdf")},
            headers=auth_headers
        )
        assert r.status_code == 400

    def test_rejects_fake_pdf(self, client, auth_headers):
        """A file named .pdf but with wrong magic bytes should be rejected."""
        r = client.post(
            "/api/resume/analyze",
            files={"file": ("fake.pdf", b"NOT_A_PDF_CONTENT_HERE!!" * 5, "application/pdf")},
            headers=auth_headers
        )
        assert r.status_code == 400
        assert "doesn't match PDF format" in r.json()["detail"]


class TestJDMatchAPI:
    def test_rejects_short_resume(self, client, auth_headers):
        r = client.post(
            "/api/jd/match",
            json={"resume_text": "short", "jd_text": "This is a proper job description for testing"},
            headers=auth_headers
        )
        assert r.status_code == 400

    def test_rejects_short_jd(self, client, auth_headers):
        r = client.post(
            "/api/jd/match",
            json={"resume_text": "Python developer with 5 years of experience in building web applications", "jd_text": "short"},
            headers=auth_headers
        )
        assert r.status_code == 400


class TestFeedbackAPI:
    def test_submit_feedback(self, client, auth_headers):
        r = client.post("/api/feedback/", json={
            "rating": 4.5,
            "category": "general",
            "comment": "Great tool!"
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["rating"] == 4.5

    def test_submit_feedback_invalid_rating(self, client, auth_headers):
        r = client.post("/api/feedback/", json={
            "rating": 6,
            "category": "general",
        }, headers=auth_headers)
        assert r.status_code == 422  # Pydantic validation

    def test_get_feedback_history(self, client, auth_headers):
        r = client.get("/api/feedback/", headers=auth_headers)
        assert r.status_code == 200
        assert "feedbacks" in r.json()


class TestHistoryAPI:
    def test_get_history_empty(self, client, auth_headers):
        r = client.get("/api/history/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "analyses" in data
        assert "total" in data

    def test_get_history_requires_auth(self, client):
        r = client.get("/api/history/")
        assert r.status_code == 401

    def test_get_nonexistent_analysis(self, client, auth_headers):
        r = client.get("/api/history/nonexistent-id", headers=auth_headers)
        assert r.status_code == 404
