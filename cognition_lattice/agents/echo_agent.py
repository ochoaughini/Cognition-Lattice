from typing import Dict, Any
from ..base_agent import BaseAgent

class EchoAgent(BaseAgent):
    """Simple agent that echoes arguments."""

    intent_types = ["echo"]

    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ok", "echo": intent.get("args")}
