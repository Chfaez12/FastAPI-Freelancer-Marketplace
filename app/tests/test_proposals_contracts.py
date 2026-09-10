
def test_proposal_creation_and_duplicate_prevention(client, job, freelancer_headers):
    payload = {
        "cover_letter": "I can deliver this project.",
        "bid_amount": 900,
        "estimated_duration": "5 days",
    }
    first = client.post(
        f"/jobs/{job['id']}/proposals",
        headers=freelancer_headers,
        json=payload,
    )
    assert first.status_code in (200, 201)

    duplicate = client.post(
        f"/jobs/{job['id']}/proposals",
        headers=freelancer_headers,
        json=payload,
    )
    assert duplicate.status_code in (400, 409)


def test_client_accepting_proposal_creates_contract(client, proposal, client_headers):
    response = client.post(
        f"/proposals/{proposal['id']}/accept",
        headers=client_headers,
    )
    assert response.status_code in (200, 201)
    assert response.json()["id"]
    assert response.json().get("status", "ACTIVE") in ("ACTIVE", "PENDING")


def test_milestone_workflow_rejects_invalid_transition(
    client, proposal, client_headers, freelancer_headers
):
    contract = client.post(
        f"/proposals/{proposal['id']}/accept",
        headers=client_headers,
    )
    assert contract.status_code in (200, 201)
    contract_id = contract.json()["id"]

    milestone = client.post(
        f"/contracts/{contract_id}/milestones",
        headers=client_headers,
        json={"title": "First delivery", "amount": 950},
    )
    assert milestone.status_code in (200, 201)
    milestone_id = milestone.json()["id"]

    early_review = client.post(
        f"/milestones/{milestone_id}/review",
        headers=client_headers,
        json={"action": "APPROVED"},
    )
    assert early_review.status_code in (400, 409, 422)

    submitted = client.post(
        f"/milestones/{milestone_id}/submit",
        headers=freelancer_headers,
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "SUBMITTED"


def test_contract_cannot_complete_before_all_milestones_are_approved(
    client, proposal, client_headers
):
    contract = client.post(
        f"/proposals/{proposal['id']}/accept",
        headers=client_headers,
    )
    assert contract.status_code in (200, 201)
    milestone = client.post(
        f"/contracts/{contract.json()['id']}/milestones",
        headers=client_headers,
        json={"title": "Incomplete work", "amount": 950},
    )
    assert milestone.status_code in (200, 201)

    response = client.post(
        f"/contracts/{contract.json()['id']}/complete",
        headers=client_headers,
    )
    assert response.status_code in (400, 409, 422)

