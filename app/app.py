# app/app.py
from flask import Flask, request, jsonify
from app.keys import KeyStore
import jwt
import time

app = Flask(__name__)
keystore = KeyStore()

@app.route("/auth", methods=["POST"])
def auth():
    """Sign a JWT using a valid or expired key."""
    expired_flag = request.args.get("expired", "").lower() in ("1", "true", "yes")
    key = keystore.get_for_signing(expired=expired_flag)

    if not key:
        return jsonify({"error": "no signing key available"}), 500

    payload = {
        "sub": "userABC",
        "iat": int(time.time()),
        "iss": "https://your-jwks-server.example"
    }

    token = jwt.encode(
        payload,
        key.jwk_obj.export_to_pem(private_key=True, password=None),
        algorithm="RS256",
        headers={"kid": key.kid}
    )
    return jsonify({"token": token})

@app.route("/.well-known/jwks.json", methods=["GET"])
def jwks():
    """Return all valid JWKs as a JWKS set."""
    valid_keys = keystore.active_keys()
    public_keys = [k.export_public(as_dict=True) for k in valid_keys]
    return jsonify({"keys": public_keys})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
