"""RabbitMQ broker implementation."""

from typing import Dict, Any, Generator
import json
import pika

from .broker import BrokerClient


class RabbitMQBroker(BrokerClient):
    def __init__(self, url: str) -> None:
        params = pika.URLParameters(url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue="intents", durable=True)
        self._channel.queue_declare(queue="responses", durable=True)

    def send_intent(self, intent: Dict[str, Any]) -> None:
        self._channel.basic_publish(
            exchange="",
            routing_key="intents",
            body=json.dumps(intent).encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def receive_intents(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        method_frame, _, body = self._channel.basic_get("intents", auto_ack=False)
        if method_frame:
            yield json.loads(body)
            self._channel.basic_ack(method_frame.delivery_tag)

    def acknowledge_intent(self, intent: Dict[str, Any]) -> None:
        pass

    def publish_response(self, response: Dict[str, Any]) -> None:
        self._channel.basic_publish(
            exchange="",
            routing_key="responses",
            body=json.dumps(response).encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def receive_responses(self, timeout: float = 1.0) -> Generator[Dict[str, Any], None, None]:
        method_frame, _, body = self._channel.basic_get("responses", auto_ack=True)
        if method_frame:
            yield json.loads(body)
