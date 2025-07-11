"""HTTP utilities for agents."""

from typing import Any, Dict
import requests


def get(url: str, **kwargs: Any) -> Dict[str, Any]:
    resp = requests.get(url, **kwargs)
    return {"status": resp.status_code, "content": resp.text}
