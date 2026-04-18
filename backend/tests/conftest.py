"""
Shared test fixtures for the AI Resume Analyzer test suite.
"""
import os
os.environ["TESTING"] = "true"  # Disable rate limiting during tests

import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_resume_analyzer.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before tests and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a clean DB session per test, rollback after."""
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session):
    """TestClient with overridden DB dependency."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    """Create a test user and return a JWT token."""
    r = client.post("/auth/signup", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPass123"
    })
    if r.status_code == 200:
        return r.json().get("token")
    # User might already exist — try login
    r = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "TestPass123"
    })
    return r.json().get("token")


@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}


# ── Sample text fixtures ──

SAMPLE_RESUME_TEXT = """
John Doe
john.doe@gmail.com | +91 9876543210
linkedin.com/in/johndoe | github.com/johndoe

Professional Summary
Experienced Full Stack Developer with 5+ years of experience building
scalable web applications using React, Node.js, and Python.

Experience
Senior Software Engineer — TechCorp Inc. (2020 - Present)
• Developed and deployed microservices architecture serving 2M+ users
• Reduced API response time by 40% through Redis caching optimization
• Led a team of 5 engineers in migrating legacy monolith to cloud-native stack

Software Engineer — StartupXYZ (2018 - 2020)
• Built RESTful APIs using Django and Flask, handling 500K daily requests
• Implemented CI/CD pipelines reducing deployment time from 2 hours to 15 minutes
• Collaborated with product team to ship 12 features in 6 months

Education
B.Tech in Computer Science — IIT Delhi (2014 - 2018)
GPA: 8.7/10

Skills
Python, JavaScript, TypeScript, React, Node.js, Django, Flask, PostgreSQL,
MongoDB, Redis, Docker, Kubernetes, AWS, Git, CI/CD, Agile

Certifications
AWS Solutions Architect Associate (2022)
"""

SAMPLE_JD_TEXT = """
We are looking for a Senior Full Stack Developer to join our team.

Requirements:
- 4+ years of experience in full stack development
- Proficiency in React, Node.js, and Python
- Experience with cloud services (AWS/GCP/Azure)
- Strong understanding of RESTful APIs and microservices
- Experience with Docker and Kubernetes
- Familiarity with CI/CD pipelines
- Strong problem-solving skills
- Excellent communication skills

Nice to have:
- Experience with TypeScript
- Knowledge of GraphQL
- Experience with Redis or similar caching systems
"""
