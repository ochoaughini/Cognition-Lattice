"""Simple vector store built on FAISS."""

from typing import Any, Iterable

try:
    import faiss
except ImportError:  # pragma: no cover - optional dependency
    faiss = None

from .memory_interface import MemoryClient


class VectorMemory(MemoryClient):
    def __init__(self, dim: int) -> None:
        if faiss is None:
            raise RuntimeError("faiss is required for VectorMemory")
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.data: list[Any] = []

    def put(self, key: str, value: Any) -> None:
        vector = value["vector"]
        if len(vector) != self.dim:
            raise ValueError("Vector dimension mismatch")
        self.index.add(vector.reshape(1, -1))
        self.data.append(value)

    def get(self, key: str) -> Any:
        raise NotImplementedError("VectorMemory does not support get by key")

    def delete(self, key: str) -> None:
        raise NotImplementedError("VectorMemory does not support delete by key")

    def search(self, query: str | Iterable[float]) -> Iterable[Any]:
        import numpy as np

        if isinstance(query, str):
            raise ValueError("Vector query expected")
        q = np.array(query).reshape(1, -1)
        _, idx = self.index.search(q, 5)
        for i in idx[0]:
            if i < len(self.data):
                yield self.data[i]
