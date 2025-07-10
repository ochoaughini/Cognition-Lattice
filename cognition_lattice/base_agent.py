from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Base class for all executor agents."""

    @abstractmethod
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intent and return result."""
        raise NotImplementedError
