"""Simple schema registry."""

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=128)
def load_schema(path: str) -> dict:
    return json.loads(Path(path).read_text())
