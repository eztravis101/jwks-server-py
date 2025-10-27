from __future__ import annotations
from dataclasses import dataclass
from typing import List
import time
import hashlib
import base64
from jwcrypto import jwk
from app.db import init_db, store_key

@dataclass
class Key:
    jwk_obj: jwk.JWK
    kid: str
    expires_at: int

class KeyStore:
    def __init__(self) -> None:
        init_db()
        now = int(time.time())
        self.active = self._generate(expires_at=now + 3600)
        self.expired = self._generate(expires_at=now - 3600)
        self._persist_keys()

    def _generate(self, *, expires_at: int) -> Key:
        key = jwk.JWK.generate(kty="RSA", size=2048)
        pub = key.export_public(as_dict=True)
        n_b64 = pub.get("n", "").encode("utf-8")
        kid = base64.urlsafe_b64encode(hashlib.sha1(n_b64).digest()).rstrip(b"=").decode("ascii")
        key["kid"] = kid
        return Key(jwk_obj=key, kid=kid, expires_at=expires_at)

    def _persist_keys(self):
        for k in [self.active, self.expired]:
            pub = k.jwk_obj.export_public(as_dict=True)
            priv_pem = k.jwk_obj.export_to_pem(private_key=True, password=None).decode("utf-8")
            store_key(                     # ✅ removed expires_at
                kid=k.kid,
                n=pub.get("n", ""),
                e=pub.get("e", ""),
                d=priv_pem
            )

    def active_keys(self, now: int | None = None) -> List[jwk.JWK]:
        now = now or int(time.time())
        keys: List[jwk.JWK] = []
        if self.active and self.active.expires_at > now:
            keys.append(self.active.jwk_obj)
        return keys

    def get_for_signing(self, *, expired: bool) -> Key:
        return self.expired if expired else self.active
