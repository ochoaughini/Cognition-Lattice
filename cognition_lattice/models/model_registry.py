"""Register and retrieve ML models."""

from typing import Dict, Any
from importlib import import_module

from .model_client import ModelClient


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, ModelClient] = {}

    def register(self, name: str, path: str, cls: str, **kwargs: Any) -> None:
        module = import_module(path)
        model_cls = getattr(module, cls)
        self._models[name] = model_cls(**kwargs)

    def get(self, name: str) -> ModelClient:
        return self._models[name]
