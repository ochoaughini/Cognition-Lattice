"""Utilities for persistence and TTL cleanup."""

import time
from typing import Any


class MemoryPersistence:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def put(self, key: str, value: Any, ttl: float | None = None) -> None:
        expiry = time.time() + ttl if ttl else 0
        self._store[key] = (value, expiry)

    def get(self, key: str) -> Any:
        value, expiry = self._store.get(key, (None, 0))
        if expiry and expiry < time.time():
            self._store.pop(key, None)
            return None
        return value

    def cleanup(self) -> None:
        now = time.time()
        for key, (_, expiry) in list(self._store.items()):
            if expiry and expiry < now:
                self._store.pop(key, None)
