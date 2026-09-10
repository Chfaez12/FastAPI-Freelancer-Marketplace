import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "StrongPassword123!", "name": "Invalid", "role": "CLIENT"},
        {"password": "StrongPassword123!", "name": "Invalid", "role": "CLIENT"},
        {"email": "valid@example.com", "name": "Invalid", "role": "CLIENT"},
        {"email": "valid@example.com", "password": "StrongPassword123!", "name": "Invalid", "role": "UNKNOWN"},
    ],
)
def test_registration_validation_errors(client, payload):
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_missing_required_job_fields_are_rejected(client, client_headers):
    response = client.post(
        "/jobs",
        headers=client_headers,
        json={"title": "", "budget": -1},
    )
    assert response.status_code == 422
