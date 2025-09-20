from __future__ import annotations
from dataclasses import dataclass
from typing import List
import time
import hashlib
import base64
from jwcrypto import jwk

@dataclass
class Key:
    jwk_obj: jwk.JWK
    kid: str
    expires_at: int  # unix epoch seconds

class KeyStore:
    """In-memory keystore with one active and one expired key for demo/testing."""

    def __init__(self) -> None:
        now = int(time.time())
        self.active = self._generate(expires_at=now + 24 * 3600)
        self.expired = self._generate(expires_at=now - 3600)

    def _generate(self, *, expires_at: int) -> Key:
        key = jwk.JWK.generate(kty="RSA", size=2048)
        # kid: base64url(SHA1(modulus))
        pub = key.export_public(as_dict=True)
        n_b64 = pub.get("n", "").encode("utf-8")
        kid = base64.urlsafe_b64encode(hashlib.sha1(n_b64).digest()).rstrip(b"=").decode("ascii")
        key["kid"] = kid
        return Key(jwk_obj=key, kid=kid, expires_at=expires_at)

    def active_keys(self, now: int | None = None) -> List[jwk.JWK]:
        now = now or int(time.time())
        keys: List[jwk.JWK] = []
        if self.active and self.active.expires_at > now:
            keys.append(self.active.jwk_obj.export_public(as_dict=False))  # cloned export
            # We return a JSON string for safety, but handlers will export to dict.
        return [self.active.jwk_obj] if keys else []

    def get_for_signing(self, *, expired: bool) -> Key:
        return self.expired if expired else self.active
