def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_signup_login_refresh_and_profile(client):
    signup = client.post(
        "/signup",
        json={"name": "Grace Hopper", "email": "grace@example.com", "password": "strongpass123"},
    )
    assert signup.status_code == 201
    tokens = signup.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    login = client.post("/login", json={"email": "grace@example.com", "password": "strongpass123"})
    assert login.status_code == 200

    profile = client.get("/profile", headers=auth_header(login.json()["access_token"]))
    assert profile.status_code == 200
    assert profile.json()["email"] == "grace@example.com"

    refreshed = client.post("/refresh", params={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


def test_duplicate_signup_is_rejected(client):
    payload = {"name": "Alan Turing", "email": "alan@example.com", "password": "strongpass123"}
    assert client.post("/signup", json=payload).status_code == 201
    duplicate = client.post("/signup", json=payload)
    assert duplicate.status_code == 409