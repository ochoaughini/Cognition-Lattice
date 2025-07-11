#!/usr/bin/env python3
"""FastAPI gateway for submitting intents."""

from fastapi import FastAPI, HTTPException, Request, WebSocket
import asyncio
from pydantic import BaseModel
import uvicorn

import sios_messaging as messaging
from validation import validate_intent
from jsonschema import ValidationError

app = FastAPI()


def _wait_for_response(intent_id: str, timeout: float = 30.0):
    """Block until a response for the given intent_id is received."""
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        for resp in messaging.receive_responses(timeout=1.0):
            if resp.get("intent_id") == intent_id:
                return resp
        time.sleep(0.1)
    return None

class IntentModel(BaseModel):
    intent: str
    args: str | None = None
    intent_id: str

@app.post("/intents")
async def create_intent(intent: IntentModel, request: Request):
    data = intent.dict()
    try:
        validate_intent(data)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    messaging.send_intent(data)
    return {"status": "queued", "intent_id": intent.intent_id}


@app.websocket("/ws/{intent_id}")
async def intent_ws(websocket: WebSocket, intent_id: str):
    await websocket.accept()
    try:
        resp = await asyncio.to_thread(_wait_for_response, intent_id)
        if resp:
            await websocket.send_json(resp)
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
