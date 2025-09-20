from __future__ import annotations
from fastapi.testclient import TestClient
from jwcrypto import jwt, jwk
import time
from app.main import app
from app.routes import ks

client = TestClient(app)

def test_jwks_only_active():
    r = client.get("/.well-known/jwks.json")
    assert r.status_code == 200
    doc = r.json()
    assert "keys" in doc
    assert len(doc["keys"]) == 1
    assert doc["keys"][0]["kid"] == ks.active.kid
    assert doc["keys"][0]["kid"] != ks.expired.kid

def decode_without_verify(token: str) -> dict:
    t = jwt.JWT(jwt=token)  # parse compact
    # header is available via token.token.header, but jwcrypto hides it;
    # we'll decode header by splitting token (safe for tests)
    import json, base64
    parts = token.split(".")
    header = json.loads(base64.urlsafe_b64decode(parts[0] + "==").decode())
    claims = json.loads(t.claims)
    return {"header": header, "claims": claims}

def test_auth_post_only():
    r = client.get("/auth")
    assert r.status_code == 405  # FastAPI auto 405

def test_auth_returns_valid_jwt_and_kid():
    r = client.post("/auth")
    assert r.status_code == 200
    data = r.json()
    token = data["token"]
    kid = data["kid"]
    assert kid == ks.active.kid

    decoded = decode_without_verify(token)
    assert decoded["header"]["kid"] == ks.active.kid
    assert decoded["header"]["alg"] == "RS256"
    assert decoded["claims"]["exp"] > int(time.time())

    # Verify signature using active public key
    pub = jwk.JWK.from_json(ks.active.jwk_obj.export_public())
    v = jwt.JWT(jwt=token, key=pub)  # will raise on invalid
    assert v is not None

def test_auth_expired_param_issues_expired_token():
    r = client.post("/auth?expired=1")
    assert r.status_code == 200
    data = r.json()
    token = data["token"]
    kid = data["kid"]
    assert kid == ks.expired.kid

    decoded = decode_without_verify(token)
    assert decoded["header"]["kid"] == ks.expired.kid
    assert decoded["claims"]["exp"] < int(time.time())

    # Signature verifies with expired public key (exp is in claims, not crypto)
    pub = jwk.JWK.from_json(ks.expired.jwk_obj.export_public())
    try:
        jwt.JWT(jwt=token, key=pub)
    except Exception as e:
        # jwcrypto validates signature only (not exp) during this call, so it shouldn't fail.
        raise AssertionError(f"Token failed signature verification: {e}")
