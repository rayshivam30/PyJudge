def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_create_problem_and_samples_are_public(client, admin_token):
    response = client.post(
        "/problem",
        headers=auth_header(admin_token),
        json={
            "title": "Echo",
            "description": "Print the input.",
            "constraints": "Input is one line.",
            "difficulty": "Easy",
            "time_limit": 1,
            "memory_limit": 64,
            "tags": "strings",
            "test_cases": [
                {"input": "hello\n", "expected_output": "hello\n", "is_hidden": False},
                {"input": "secret\n", "expected_output": "secret\n", "is_hidden": True},
            ],
        },
    )
    assert response.status_code == 201
    problem_id = response.json()["id"]

    listing = client.get("/problems")
    assert listing.status_code == 200
    assert listing.json()[0]["title"] == "Echo"

    samples = client.get(f"/problem/{problem_id}/samples")
    assert samples.status_code == 200
    assert len(samples.json()) == 1
    assert samples.json()[0]["input"] == "hello\n"


def test_non_admin_cannot_create_problem(client, user_token):
    response = client.post(
        "/problem",
        headers=auth_header(user_token),
        json={"title": "Nope", "description": "x", "test_cases": []},
    )
    assert response.status_code == 403