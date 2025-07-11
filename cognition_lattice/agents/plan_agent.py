from typing import Dict, Any
from ..base_agent import BaseAgent


class PlanAgent(BaseAgent):
    intent_types = ["plan"]

    def __init__(self) -> None:
        self.rolled_back = False

    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "planned", "id": intent.get("intent_id")}

    def rollback(self, intent: Dict[str, Any]) -> None:
        self.rolled_back = True
