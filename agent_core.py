#!/usr/bin/env python3
"""Central orchestration unit for S.I.O.S."""

import json
import time
import sys
import importlib
from pathlib import Path
from typing import Dict, Any, Type
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from cognition_lattice.base_agent import BaseAgent

AGENTS_DIR = Path(__file__).parent / "cognition_lattice" / "agents"
INTENTS_DIR = Path(__file__).parent / "cognition_lattice" / "intents"
RESPONSES_DIR = Path(__file__).parent / "cognition_lattice" / "responses"

class AgentCore:
    def __init__(self) -> None:
        self.registry: Dict[str, Type[BaseAgent]] = {}
        self._load_agents()
        self._start_watcher()

    def _start_watcher(self) -> None:
        """Start filesystem watcher for hot-reloading agents."""
        handler = _AgentEventHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, str(AGENTS_DIR), recursive=False)
        self._observer.start()

    def _load_agents(self) -> None:
        """(Re)load agent modules and rebuild the registry."""
        self.registry.clear()
        modules = {}
        for path in AGENTS_DIR.glob("*.py"):
            if path.name == "__init__.py":
                continue
            module_name = f"cognition_lattice.agents.{path.stem}"
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            modules[module_name] = module
            for obj in module.__dict__.values():
                if isinstance(obj, type) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    for intent_type in getattr(obj, "intent_types", []):
                        self.registry[intent_type] = obj
        # Remove deleted modules from sys.modules
        for name in [m for m in sys.modules if m.startswith("cognition_lattice.agents.")]:
            if name not in modules:
                sys.modules.pop(name)

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
        try:
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
        finally:
            if hasattr(self, "_observer"):
                self._observer.stop()
                self._observer.join()

class _AgentEventHandler(FileSystemEventHandler):
    """Watch agent directory for changes and reload on modifications."""

    def __init__(self, core: "AgentCore") -> None:
        self.core = core

    def on_any_event(self, event) -> None:
        if event.src_path.endswith(".py"):
            self.core._load_agents()

if __name__ == "__main__":
    AgentCore().loop()
