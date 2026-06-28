def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


ACCEPTED_CODE = "a,b=map(int,input().split()); print(a+b)"
WRONG_CODE = "print(0)"
SLOW_CODE = "while True: pass"


def test_run_samples_returns_accepted(client, user_token, sample_problem):
    response = client.post(
        "/run",
        headers=auth_header(user_token),
        json={"problem_id": sample_problem.id, "language": "python", "source_code": ACCEPTED_CODE},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Accepted"
    assert body["cases"][0]["actual_output"] == "5\n"


def test_run_samples_returns_wrong_answer(client, user_token, sample_problem):
    response = client.post(
        "/run",
        headers=auth_header(user_token),
        json={"problem_id": sample_problem.id, "language": "python", "source_code": WRONG_CODE},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Wrong Answer"


def test_submit_falls_back_to_inline_judge_and_updates_history(client, user_token, sample_problem):
    response = client.post(
        "/submit",
        headers=auth_header(user_token),
        json={"problem_id": sample_problem.id, "language": "python", "source_code": ACCEPTED_CODE},
    )
    assert response.status_code == 202
    submission_id = response.json()["id"]

    detail = client.get(f"/submission/{submission_id}", headers=auth_header(user_token))
    assert detail.status_code == 200
    assert detail.json()["status"] == "Accepted"

    history = client.get("/history", headers=auth_header(user_token))
    assert history.status_code == 200
    assert history.json()[0]["id"] == submission_id

    leaderboard = client.get("/leaderboard")
    assert leaderboard.status_code == 200
    assert leaderboard.json()[0]["problems_solved"] == 1


def test_unsupported_language_returns_compilation_error(client, user_token, sample_problem):
    response = client.post(
        "/run",
        headers=auth_header(user_token),
        json={"problem_id": sample_problem.id, "language": "javascript", "source_code": "console.log(5)"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Compilation Error"