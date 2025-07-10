#!/usr/bin/env python3
"""FastAPI gateway for submitting intents."""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

import sios_messaging as messaging
from validation import validate_intent
from jsonschema import ValidationError

app = FastAPI()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
