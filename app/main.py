from __future__ import annotations
from fastapi import FastAPI
from .routes import router

app = FastAPI(title="JWKS Server (Python)")
app.include_router(router)

# Uvicorn entrypoint:
# uvicorn app.main:app --port 8080
