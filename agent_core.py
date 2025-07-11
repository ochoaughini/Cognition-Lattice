#!/usr/bin/env python3
"""Central orchestration unit for S.I.O.S."""

import json
import time
import sys
import importlib
from pathlib import Path
from typing import Dict, Any, Type, Callable, List
from dataclasses import dataclass
import asyncio
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jsonschema import ValidationError

import sios_messaging as messaging
from validation import validate_intent
from metrics import (
    intents_received,
    intents_success,
    intents_failure,
    intent_duration,
    start_metrics_server,
)

from cognition_lattice.base_agent import BaseAgent
from messaging_bus import MessageBus, Message

AGENTS_DIR = Path(__file__).parent / "cognition_lattice" / "agents"

class AgentCore:
    def __init__(self) -> None:
        self.registry: Dict[str, Type[BaseAgent]] = {}
        self._load_agents()
        self._start_watcher()
        start_metrics_server()

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
        try:
            while True:
                for intent in messaging.receive_intents(timeout=0.1):
                    intent_type = intent.get("intent", "unknown")
                    intents_received.labels(intent_type=intent_type).inc()
                    try:
                        validate_intent(intent)
                        with intent_duration.labels(intent_type=intent_type).time():
                            result = self.dispatch(intent)
                        intents_success.labels(intent_type=intent_type).inc()
                    except ValidationError as exc:
                        result = {"status": "error", "message": f"Validation error: {exc}"}
                        intents_failure.labels(intent_type=intent_type).inc()
                    except Exception as exc:
                        result = {"status": "error", "message": str(exc)}
                        intents_failure.labels(intent_type=intent_type).inc()
                    if 'intent_id' not in result and 'intent_id' in intent:
                        result['intent_id'] = intent['intent_id']
                    messaging.publish_response(result)
                    messaging.acknowledge_intent(intent)
                time.sleep(0.1)
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


@dataclass
class AgentContext:
    """Context provided to async agents."""

    mesh: "AgentMesh"
    manifest: Dict[str, Any]


class AgentMesh:
    """Simple async agent orchestrator using MessageBus."""

    def __init__(self, manifest_dir: str) -> None:
        self.manifest_dir = Path(manifest_dir)
        self.message_bus = MessageBus()
        self.manifests: List[Dict[str, Any]] = []
        self.tasks: List[asyncio.Task] = []
        self._load_manifests()

    def _load_manifests(self) -> None:
        if not self.manifest_dir.exists():
            logging.warning("Manifest directory %s does not exist", self.manifest_dir)
            return
        for path in self.manifest_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                self.manifests.append(data)
            except Exception as exc:
                logging.error("Failed to load manifest %s: %s", path, exc)

    async def start(self) -> None:
        for manifest in self.manifests:
            module = importlib.import_module(manifest["module"])
            func: Callable[[Message, AgentContext], Any] = getattr(module, manifest.get("function", "main"))
            context = AgentContext(self, manifest)
            task = asyncio.create_task(self._run_agent(func, manifest, context))
            self.tasks.append(task)

    async def _run_agent(self, func: Callable[[Message, AgentContext], Any], manifest: Dict[str, Any], context: AgentContext) -> None:
        patterns = manifest.get("subscriptions", [])
        async for message in self.message_bus.subscribe(patterns):
            try:
                result = await func(message, context)
                if isinstance(result, Message):
                    await self.message_bus.publish(f"response.{message.message_id}", result)
            except Exception:
                logging.exception("Agent %s failed", manifest.get("id"))

    async def stop(self) -> None:
        for task in list(self.tasks):
            task.cancel()
        for task in list(self.tasks):
            try:
                await task
            except asyncio.CancelledError:
                pass
        await self.message_bus.close()

if __name__ == "__main__":
    AgentCore().loop()
