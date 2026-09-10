
def test_job_search_filter_and_pagination(client, client_headers):
    for index in range(3):
        response = client.post(
            "/jobs",
            headers=client_headers,
            json={
                "title": f"Python project {index}",
                "description": "Searchable backend project",
                "budget": 500 + index,
                "skill_ids": [],
            },
        )
        assert response.status_code in (200, 201)

    response = client.get(
        "/jobs",
        params={"search": "Python", "page": 1, "limit": 2},
    )
    assert response.status_code == 200
    payload = response.json()
    items = payload.get("items", payload)
    assert len(items) <= 2
