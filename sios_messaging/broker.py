from abc import ABC, abstractmethod
from typing import Dict, Any, Generator

class BrokerClient(ABC):
    @abstractmethod
    def send_intent(self, intent: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def receive_intents(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def acknowledge_intent(self, intent: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def publish_response(self, response: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def receive_responses(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        pass
