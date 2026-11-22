def test_login_success(client):
    resp = client.post(
        "/users/login", json={"username": "admin", "password": "admin123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    resp = client.post(
        "/users/login", json={"username": "admin", "password": "wrong"}
    )
    assert resp.status_code == 401
