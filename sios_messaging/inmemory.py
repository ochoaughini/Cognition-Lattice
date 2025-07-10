from typing import Dict, Any, Generator
from queue import Queue, Empty
from .broker import BrokerClient

class InMemoryBroker(BrokerClient):
    def __init__(self) -> None:
        self._intent_queue: Queue = Queue()
        self._response_queue: Queue = Queue()

    def send_intent(self, intent: Dict[str, Any]) -> None:
        self._intent_queue.put(intent)

    def receive_intents(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        while True:
            try:
                intent = self._intent_queue.get(timeout=timeout)
                yield intent
            except Empty:
                break

    def acknowledge_intent(self, intent: Dict[str, Any]) -> None:
        # no-op for in-memory
        pass

    def publish_response(self, response: Dict[str, Any]) -> None:
        self._response_queue.put(response)

    def receive_responses(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        while True:
            try:
                resp = self._response_queue.get(timeout=timeout)
                yield resp
            except Empty:
                break
