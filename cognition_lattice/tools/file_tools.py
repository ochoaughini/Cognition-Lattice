"""File system helpers."""

from pathlib import Path
from typing import Any


def read_text(path: str) -> str:
    return Path(path).read_text()


def write_text(path: str, content: str) -> None:
    Path(path).write_text(content)
