from __future__ import annotations
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from jwcrypto import jwt
import time
from .keys import KeyStore

router = APIRouter()
ks = KeyStore()

@router.get("/.well-known/jwks.json")
def jwks() -> JSONResponse:
    # Only return non-expired public keys
    now = int(time.time())
    keys = []
    if ks.active.expires_at > now:
        keys.append(ks.active.jwk_obj.export_public(as_dict=True))
    return JSONResponse({"keys": keys})

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
