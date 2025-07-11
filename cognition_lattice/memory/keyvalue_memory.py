"""Simple key-value memory using SQLite."""

import sqlite3
import pickle
from typing import Any, Iterable

from .memory_interface import MemoryClient


class KeyValueMemory(MemoryClient):
    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value BLOB)"
        )

    def put(self, key: str, value: Any) -> None:
        self.conn.execute(
            "REPLACE INTO kv (key, value) VALUES (?, ?)", (key, sqlite3.Binary(pickle.dumps(value)))
        )
        self.conn.commit()

    def get(self, key: str) -> Any:
        cur = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,))
        row = cur.fetchone()
        return pickle.loads(row[0]) if row else None

    def delete(self, key: str) -> None:
        self.conn.execute("DELETE FROM kv WHERE key=?", (key,))
        self.conn.commit()

    def search(self, query: str) -> Iterable[Any]:
        cur = self.conn.execute("SELECT value FROM kv WHERE key LIKE ?", (f"%{query}%",))
        for row in cur.fetchall():
            yield pickle.loads(row[0])
