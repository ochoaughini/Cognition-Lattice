"""Kafka broker implementation."""

from typing import Dict, Any, Generator
import json
from kafka import KafkaProducer, KafkaConsumer

from .broker import BrokerClient


class KafkaBroker(BrokerClient):
    def __init__(self, bootstrap_servers: str) -> None:
        self._producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self._consumer = KafkaConsumer(
            "intents",
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="sios",
        )
        self._response_consumer = KafkaConsumer(
            "responses",
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="sios-resp",
        )

    def send_intent(self, intent: Dict[str, Any]) -> None:
        self._producer.send("intents", json.dumps(intent).encode())
        self._producer.flush()

    def receive_intents(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        for msg in self._consumer.poll(timeout_ms=int(timeout * 1000)).values():
            for record in msg:
                yield json.loads(record.value)

    def acknowledge_intent(self, intent: Dict[str, Any]) -> None:
        pass

    def publish_response(self, response: Dict[str, Any]) -> None:
        self._producer.send("responses", json.dumps(response).encode())
        self._producer.flush()

    def receive_responses(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        for msg in self._response_consumer.poll(timeout_ms=int(timeout * 1000)).values():
            for record in msg:
                yield json.loads(record.value)
