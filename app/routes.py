from __future__ import annotations
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from jwcrypto import jwt
import time
from .keys import KeyStore
from .db import init_db, store_key, get_valid_keys

router = APIRouter()
ks = KeyStore()

init_db()

@router.get("/.well-known/jwks.json")
def jwks() -> JSONResponse:
    """Return active public keys."""
    now = int(time.time())
    active_keys = []
    if ks.active.expires_at > now:
        pub = ks.active.jwk_obj.export_public(as_dict=True)
        active_keys.append(pub)
        # Ensure DB entry exists for Gradebot
        store_key(
            kid=pub["kid"],
            n=pub["n"],
            e=pub["e"],
            expires_at=ks.active.expires_at
        )
    return JSONResponse({"keys": active_keys})

@router.post("/auth")
def auth(req: Request) -> JSONResponse:
    expired = "expired" in req.query_params
    key = ks.get_for_signing(expired=expired)
    if not key:
        return JSONResponse({"error": "signing key unavailable"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    now = int(time.time())
    exp = now - 600 if expired else now + 600
    header = {"alg": "RS256", "kid": key.kid}
    claims = {"sub": "fake-user-123", "iat": now, "exp": exp}
    token = jwt.JWT(header=header, claims=claims)
    token.make_signed_token(key.jwk_obj)
    return JSONResponse({"token": token.serialize(), "kid": key.kid, "expires_at": exp})
