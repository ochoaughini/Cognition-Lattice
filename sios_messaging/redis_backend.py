import json
from typing import Dict, Any, Generator
import redis
from .broker import BrokerClient

class RedisBroker(BrokerClient):
    def __init__(self, url: str) -> None:
        self._client = redis.Redis.from_url(url)

    def send_intent(self, intent: Dict[str, Any]) -> None:
        self._client.lpush("intents", json.dumps(intent))

    def receive_intents(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        while True:
            item = self._client.brpop("intents", timeout=timeout)
            if item is None:
                break
            _, data = item
            yield json.loads(data)

    def acknowledge_intent(self, intent: Dict[str, Any]) -> None:
        # Redis lists do not require explicit ack
        pass

    def publish_response(self, response: Dict[str, Any]) -> None:
        self._client.lpush("responses", json.dumps(response))

    def receive_responses(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        while True:
            item = self._client.brpop("responses", timeout=timeout)
            if item is None:
                break
            _, data = item
            yield json.loads(data)
