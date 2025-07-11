from typing import Dict, Any
from ..base_agent import BaseAgent


class VerifyAgent(BaseAgent):
    intent_types = ["verify"]

    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("Verification failed")
