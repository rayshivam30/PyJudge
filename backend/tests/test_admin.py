def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_dashboard_counts_entities(client, admin_token, sample_problem):
    response = client.get("/dashboard", headers=auth_header(admin_token))
    assert response.status_code == 200
    body = response.json()
    assert body["users"] == 1
    assert body["problems"] == 1
    assert body["test_cases"] == 2


def test_admin_can_ban_user(client, admin_token, db_session):
    signup = client.post(
        "/signup",
        json={"name": "Banned User", "email": "banned@example.com", "password": "strongpass123"},
    )
    user_id = client.get("/profile", headers=auth_header(signup.json()["access_token"])).json()["id"]

    response = client.post(f"/admin/users/{user_id}/ban", headers=auth_header(admin_token))
    assert response.status_code == 200

    login = client.post("/login", json={"email": "banned@example.com", "password": "strongpass123"})
    assert login.status_code == 403