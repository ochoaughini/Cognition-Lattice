from typing import Dict, Any, Generator
from queue import Queue, Empty

_intent_queue: Queue = Queue()
_response_queue: Queue = Queue()


def send_intent(intent: Dict[str, Any]) -> None:
    _intent_queue.put(intent)


def receive_intents(timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
    while True:
        try:
            intent = _intent_queue.get(timeout=timeout)
            yield intent
        except Empty:
            break


def acknowledge_intent(intent: Dict[str, Any]) -> None:
    # noop for in-memory queue
    pass


def publish_response(response: Dict[str, Any]) -> None:
    _response_queue.put(response)


def receive_responses(timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
    while True:
        try:
            resp = _response_queue.get(timeout=timeout)
            yield resp
        except Empty:
            break
