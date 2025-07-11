"""Code parsing helpers."""

import subprocess
from pathlib import Path
from typing import Iterable


def format_code(paths: Iterable[str]) -> None:
    for path in paths:
        subprocess.run(["black", path, "-q"], check=False)
