from abc import ABC, abstractmethod
from typing import Any, Dict


class ModelClient(ABC):
    """Interface for ML model wrappers."""

    @abstractmethod
    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
