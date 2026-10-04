import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request


def create_app(secret: str, database: Path) -> FastAPI:
    app = FastAPI(title="NovaWebhookRelay")
    with sqlite3.connect(database) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, received_at TEXT DEFAULT CURRENT_TIMESTAMP, body BLOB NOT NULL)"
        )

    @app.post("/webhook", status_code=202)
    async def receive(
        request: Request, x_nova_signature: str | None = Header(default=None)
    ) -> dict[str, str]:
        body = await request.body()
        expected = (
            "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        )
        if not x_nova_signature or not hmac.compare_digest(expected, x_nova_signature):
            raise HTTPException(401, "invalid signature")
        with sqlite3.connect(database) as db:
            db.execute("INSERT INTO events(body) VALUES (?)", (body,))
        return {"status": "accepted"}

    return app


def run() -> None:
    secret = os.environ.get("NOVAWEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("NOVAWEBHOOK_SECRET is required")
    uvicorn.run(
        create_app(secret, Path(os.environ.get("NOVAWEBHOOK_DB", "events.db"))),
        host="127.0.0.1",
        port=8081,
    )
