from abc import ABC, abstractmethod
from typing import Any, Iterable

class MemoryClient(ABC):
    """Abstract base class for memory backends."""

    @abstractmethod
    def put(self, key: str, value: Any) -> None:
        """Store a value."""
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> Any:
        """Retrieve a value by key."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key from storage."""
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> Iterable[Any]:
        """Search the memory for entries matching the query."""
        raise NotImplementedError
