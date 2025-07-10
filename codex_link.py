#!/usr/bin/env python3
"""Simplified Codex Link for injecting intents."""

import json
from pathlib import Path
from typing import Any, Dict
import uuid

INTENTS_DIR = Path(__file__).parent / "cognition_lattice" / "intents"


def create_intent(intent_type: str, args: Any) -> Path:
    INTENTS_DIR.mkdir(parents=True, exist_ok=True)
    intent_id = str(uuid.uuid4())
    intent = {
        "intent": intent_type,
        "args": args,
        "intent_id": intent_id,
    }
    path = INTENTS_DIR / f"{intent_id}.json"
    path.write_text(json.dumps(intent, indent=2))
    print(f"Intent written to {path}")
    return path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Send an intent to the agent")
    parser.add_argument("intent", help="intent type")
    parser.add_argument("args", nargs="?", help="arguments", default="")
    args = parser.parse_args()
    create_intent(args.intent, args.args)
