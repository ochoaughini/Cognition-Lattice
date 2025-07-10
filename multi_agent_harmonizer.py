#!/usr/bin/env python3
"""Manage multiple agents working on tasks."""

from typing import Dict, Any, List
from cognition_lattice.base_agent import BaseAgent


class MultiAgentHarmonizer:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run_all(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for agent in self.agents:
            try:
                results.append(agent.execute(intent))
            except Exception as exc:
                results.append({"status": "error", "message": str(exc)})
        return results
