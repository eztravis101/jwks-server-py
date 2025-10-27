# app/tests/test_server.py
import pytest
from app.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_jwks_endpoint(client):
    resp = client.get("/.well-known/jwks.json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "keys" in data
    assert isinstance(data["keys"], list)
    assert len(data["keys"]) >= 1

def test_auth_valid(client):
    resp = client.post("/auth", json={"username": "userABC", "password": "password123"})
    assert resp.status_code == 200
    token = resp.get_json().get("token")
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # basic JWT shape check
