"""Store responses for async retrieval."""

from typing import Dict


class ResponseStore:
    def __init__(self) -> None:
        self._store: Dict[str, dict] = {}

    def add(self, resp: dict) -> None:
        intent_id = resp.get("intent_id")
        if intent_id:
            self._store[intent_id] = resp

    def get(self, intent_id: str) -> dict | None:
        return self._store.pop(intent_id, None)
