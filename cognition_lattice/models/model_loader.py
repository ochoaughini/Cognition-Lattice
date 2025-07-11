"""Dynamic model loader with caching."""

from functools import lru_cache
from typing import Any

from .model_registry import ModelRegistry


@lru_cache(maxsize=32)
def get_registry() -> ModelRegistry:
    return ModelRegistry()


def load_model(name: str, path: str, cls: str, **kwargs: Any) -> None:
    registry = get_registry()
    if name not in registry._models:
        registry.register(name, path, cls, **kwargs)
