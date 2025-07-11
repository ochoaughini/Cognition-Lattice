"""Validate messages with Protocol Buffers."""

from typing import Any
import importlib
from google.protobuf.message import Message


class ProtoValidator:
    def __init__(self, proto_path: str, message_name: str) -> None:
        module = importlib.import_module(proto_path)
        self.message_cls = getattr(module, message_name)

    def validate(self, data: bytes) -> Message:
        msg = self.message_cls()
        msg.ParseFromString(data)
        return msg
