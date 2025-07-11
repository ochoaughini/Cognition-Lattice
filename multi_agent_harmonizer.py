#!/usr/bin/env python3
"""Manage multiple agents working on tasks."""

from typing import Dict, Any, List
from cognition_lattice.base_agent import BaseAgent


class MultiAgentHarmonizer:
    """Run a series of agents with basic SAGA-style rollback."""

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run_all(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute agents sequentially. Roll back on failure if possible."""
        results: List[Dict[str, Any]] = []
        executed: List[BaseAgent] = []
        try:
            for agent in self.agents:
                result = agent.execute(intent)
                results.append(result)
                executed.append(agent)
                if result.get("status") == "error":
                    raise Exception(result.get("message"))
            return results
        except Exception as exc:
            for agent in reversed(executed):
                rollback = getattr(agent, "rollback", None)
                if callable(rollback):
                    try:
                        rollback(intent)
                    except Exception:
                        pass
            results.append({"status": "error", "message": str(exc)})
            return results
