#!/usr/bin/env python3
"""Central orchestration unit for S.I.O.S."""

import json
import time
from pathlib import Path
from typing import Dict, Any, Type

from cognition_lattice.base_agent import BaseAgent

AGENTS_DIR = Path(__file__).parent / "cognition_lattice" / "agents"
INTENTS_DIR = Path(__file__).parent / "cognition_lattice" / "intents"
RESPONSES_DIR = Path(__file__).parent / "cognition_lattice" / "responses"

class AgentCore:
    def __init__(self) -> None:
        self.registry: Dict[str, Type[BaseAgent]] = {}
        self._load_agents()

    def _load_agents(self) -> None:
        for path in AGENTS_DIR.glob("*.py"):
            if path.name == "__init__.py":
                continue
            module = __import__(f"cognition_lattice.agents.{path.stem}", fromlist=["*"])
            for obj in module.__dict__.values():
                if isinstance(obj, type) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    for intent_type in getattr(obj, "intent_types", []):
                        self.registry[intent_type] = obj

    def dispatch(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        intent_type = intent.get("intent")
        agent_cls = self.registry.get(intent_type)
        if not agent_cls:
            return {"status": "error", "message": f"No agent for intent {intent_type}"}
        agent = agent_cls()
        try:
            return agent.execute(intent)
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def loop(self) -> None:
        INTENTS_DIR.mkdir(parents=True, exist_ok=True)
        RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
        while True:
            for intent_file in INTENTS_DIR.glob("*.json"):
                try:
                    intent = json.loads(intent_file.read_text())
                except Exception as exc:
                    result = {"status": "error", "message": f"Invalid JSON: {exc}"}
                else:
                    result = self.dispatch(intent)
                resp_file = RESPONSES_DIR / intent_file.name
                resp_file.write_text(json.dumps(result, indent=2))
                intent_file.unlink()
            time.sleep(1)

if __name__ == "__main__":
    AgentCore().loop()
