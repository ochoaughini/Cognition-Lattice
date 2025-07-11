from typing import Dict, Any
from ..base_agent import BaseAgent


class ActAgent(BaseAgent):
    intent_types = ["act"]

    def __init__(self) -> None:
        self.rolled_back = False

    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        if intent.get("simulate_failure"):
            raise RuntimeError("Action failed")
        return {"status": "acted", "id": intent.get("intent_id")}

    def rollback(self, intent: Dict[str, Any]) -> None:
        self.rolled_back = True
