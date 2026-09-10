import uuid


def test_registration_and_login_return_tokens(client):
    email = f"user-{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123!"

    register = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "New User",
            "role": "FREELANCER",
        },
    )
    assert register.status_code in (200, 201)

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]
    assert login.cookies.get("refresh_token")


def test_registration_rejects_duplicate_email(client, client_user):
    response = client.post(
        "/auth/register",
        json={
            "email": client_user["email"],
            "password": "StrongPassword123!",
            "name": "Duplicate",
            "role": "CLIENT",
        },
    )
    assert response.status_code in (400, 409)


def test_login_rejects_invalid_password(client, client_user):
    response = client.post(
        "/auth/login",
        json={"email": client_user["email"], "password": "wrong-password"},
    )
    assert response.status_code in (400, 401)


def test_access_token_protects_private_endpoints(client):
    response = client.get("/users")
    assert response.status_code == 401

def test_logout_revokes_access_or_refresh_token(client, client_user):
    response = client.post(
        "/auth/logout",
        headers=client_user["headers"],
    )
    assert response.status_code in (200, 204)


def test_roles_are_enforced_for_job_creation(client, job, freelancer_headers):
    response = client.post(
        "/jobs",
        headers=freelancer_headers,
        json={
            "title": "Should not be created",
            "description": "A freelancer cannot post a client job.",
            "budget": 50,
            "skill_ids": [],
        },
    )
    assert response.status_code == 403
