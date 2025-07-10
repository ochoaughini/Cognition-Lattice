import os
from typing import Dict, Any, Generator

from .broker import BrokerClient
from .inmemory import InMemoryBroker
try:
    from .redis_backend import RedisBroker
except Exception:  # pragma: no cover - redis optional
    RedisBroker = None  # type: ignore


def _init_client() -> BrokerClient:
    broker = os.getenv("MESSAGE_BROKER", "inmem")
    if broker == "redis" and RedisBroker is not None:
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        return RedisBroker(url)
    return InMemoryBroker()

_client = _init_client()


def send_intent(intent: Dict[str, Any]) -> None:
    _client.send_intent(intent)


def receive_intents(timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
    yield from _client.receive_intents(timeout)


def acknowledge_intent(intent: Dict[str, Any]) -> None:
    _client.acknowledge_intent(intent)


def publish_response(response: Dict[str, Any]) -> None:
    _client.publish_response(response)


def receive_responses(timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
    yield from _client.receive_responses(timeout)
