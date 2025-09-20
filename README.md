# JWKS Server (Python / FastAPI)

A RESTful JWKS server that:
- Generates RSA key pairs with `kid` and expiry metadata.
- Serves only **non-expired** public keys at `GET /.well-known/jwks.json` (JWKS format).
- Issues JWTs at `POST /auth`.
  - Normal: signed with active key; `exp` in the future.
  - `?expired=1`: signed with expired key; `exp` in the past.
- Includes `kid` in JWT header.
- Uses proper HTTP status codes (FastAPI returns `405` on wrong method).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --port 8080
```

### Endpoints

- `GET /.well-known/jwks.json`
- `POST /auth`
- `POST /auth?expired=1`

## Tests & Coverage

```bash
make cover
```

## Linting/Formatting

```bash
make lint
make format
```

## Docker

```bash
docker build -t jwks-server-py:local .
docker run -p 8080:8080 jwks-server-py:local
```
