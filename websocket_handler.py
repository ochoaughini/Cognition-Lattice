"""Manage WebSocket connections."""

from typing import Dict
from fastapi import WebSocket


class WebSocketHandler:
    def __init__(self) -> None:
        self.connections: Dict[str, WebSocket] = {}

    async def add(self, intent_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self.connections[intent_id] = ws

    async def send(self, intent_id: str, data: dict) -> None:
        ws = self.connections.get(intent_id)
        if ws:
            await ws.send_json(data)
            await ws.close()
            self.connections.pop(intent_id, None)
