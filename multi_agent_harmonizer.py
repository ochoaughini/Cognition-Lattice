#!/usr/bin/env python3
"""Manage multiple agents working on tasks."""

from typing import Dict, Any, List, Any as AnyType
from cognition_lattice.base_agent import BaseAgent


class MultiAgentHarmonizer:
    """Execute workflow steps with SAGA-style rollback semantics."""

    def __init__(self, agents: List[BaseAgent]):
        # keep original order for fallback behaviour but build intent registry
        self._agents = agents
        self._registry = {}
        for a in agents:
            intent_types = getattr(a, "intent_types", [])
            if intent_types:
                self._registry[intent_types[0]] = a

    def run_all(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run either a workflow or a simple sequence of agents."""
        steps: List[Dict[str, Any]] = ctx.get("workflow") or None

        if steps is None:
            # legacy behaviour: run given context through each agent sequentially
            results: List[Dict[str, Any]] = []
            executed: List[BaseAgent] = []
            for agent in self._agents:
                try:
                    res = agent.execute(ctx)
                    results.append(res)
                    executed.append(agent)
                    if res.get("status") == "error":
                        raise Exception(res.get("message"))
                except Exception as exc:
                    for ag in reversed(executed):
                        rb = getattr(ag, "rollback", None)
                        if callable(rb):
                            try:
                                rb(ctx)
                            except Exception:
                                pass
                    results.append({"status": "error", "message": str(exc)})
                    break
            return results
        else:
            # resolve agent instances based on intent type in each step
            agent_order = [self._registry[s.get("intent")] for s in steps]

        executed: List[BaseAgent] = []
        results: List[Dict[str, Any]] = []

        for step, agent in zip(steps, agent_order):
            try:
                res = agent.execute(step)
                results.append(res)
                executed.append(agent)
                if res.get("status") == "error":
                    raise Exception(res.get("message"))
            except Exception as exc:
                # rollback already executed agents in reverse order
                for ag in reversed(executed):
                    rollback = getattr(ag, "rollback", None)
                    if callable(rollback):
                        try:
                            rollback(step)
                        except Exception:
                            pass
                results.append({"status": "error", "message": str(exc), "intent": step.get("intent")})
                break

        return results
