import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _unique_email(role: str) -> str:
    return f"{role.lower()}-{uuid.uuid4().hex}@example.com"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _register_and_login(client: TestClient, role: str) -> dict:
    email = _unique_email(role)
    password = "StrongPassword123!"
    register = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "name": f"Test {role.title()}",
            "role": role,
        },
    )
    assert register.status_code in (200, 201), register.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text
    payload = login.json()
    assert payload.get("access_token")
    return {
        "email": email,
        "password": password,
        "role": role,
        "access_token": payload["access_token"],
        "refresh_token": login.cookies.get("refresh_token"),
        "headers": {"Authorization": f"Bearer {payload['access_token']}"},
    }


@pytest.fixture
def client_user(client):
    return _register_and_login(client, "CLIENT")


@pytest.fixture
def freelancer_user(client):
    return _register_and_login(client, "FREELANCER")


@pytest.fixture
def client_headers(client_user):
    return client_user["headers"]


@pytest.fixture
def freelancer_headers(freelancer_user):
    return freelancer_user["headers"]


@pytest.fixture
def job(client, client_headers):
    response = client.post(
        "/jobs",
        headers=client_headers,
        json={
            "title": "Build a marketplace API",
            "description": "Create and test a production FastAPI marketplace.",
            "budget": 1000,
            "skill_ids": [],
        },
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


@pytest.fixture
def proposal(client, job, freelancer_headers):
    response = client.post(
        f"/jobs/{job['id']}/proposals",
        headers=freelancer_headers,
        json={
            "cover_letter": "I can deliver this API safely and on schedule.",
            "bid_amount": 950,
            "estimated_duration": "7 days",
        },
    )
    assert response.status_code in (200, 201), response.text
    return response.json()
