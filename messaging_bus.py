"""
Messaging bus implementation for inter-agent communication.
"""
import asyncio
import json
from enum import Enum
from typing import Dict, List, Optional, AsyncGenerator, Set, Callable, Any, Tuple
from dataclasses import dataclass, field
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """Types of messages in the system."""
    INTENT = "intent"
    EVENT = "event"
    RESPONSE = "response"
    ERROR = "error"
    SIGNAL = "signal"

@dataclass
class Message:
    """Base message class for all inter-agent communication."""
    type: MessageType
    source: str
    target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "metadata": self.metadata,
            "message_id": self.message_id,
            "correlation_id": self.correlation_id or self.message_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            type=MessageType(data['type']),
            source=data['source'],
            target=data.get('target'),
            payload=data.get('payload', {}),
            metadata=data.get('metadata', {}),
            message_id=data.get('message_id', str(uuid.uuid4())),
            correlation_id=data.get('correlation_id'),
            timestamp=data.get('timestamp', datetime.utcnow().isoformat())
        )
    
    def reply(self, payload: Dict[str, Any] = None, **kwargs) -> 'Message':
        """Create a reply message."""
        return Message(
            type=MessageType.RESPONSE,
            source=self.target or "",
            target=self.source,
            payload=payload or {},
            correlation_id=self.message_id,
            **kwargs
        )

class MessageBus:
    """
    Message bus for inter-agent communication.
    
    Supports pub/sub pattern with topic-based routing.
    """
    
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._subscriptions: Dict[str, Set[asyncio.Queue]] = {}
        self._patterns: List[Tuple[str, asyncio.Queue]] = []
        self._running = True
    
    async def publish(self, topic: str, message: Message) -> None:
        """Publish a message to a topic."""
        if not self._running:
            raise RuntimeError("Message bus is not running")
            
        if not isinstance(message, Message):
            raise ValueError("Message must be an instance of Message class")
            
        # Convert message to dict for serialization
        message_dict = message.to_dict()
        
        # Publish to direct subscribers
        for queue in self._subscriptions.get(topic, set()):
            await queue.put((topic, message_dict))
        
        # Publish to pattern subscribers
        for pattern, queue in self._patterns:
            if self._match_pattern(pattern, topic):
                await queue.put((topic, message_dict))
    
    def _match_pattern(self, pattern: str, topic: str) -> bool:
        """Check if a topic matches a pattern with wildcards."""
        pattern_parts = pattern.split('.')
        topic_parts = topic.split('.')
        
        if len(pattern_parts) != len(topic_parts):
            return False
            
        for p, t in zip(pattern_parts, topic_parts):
            if p == '*':
                continue
            if p != t:
                return False
                
        return True
    
    async def subscribe(self, patterns: List[str]) -> AsyncGenerator[Message, None]:
        """Subscribe to messages matching the given patterns."""
        if not self._running:
            raise RuntimeError("Message bus is not running")
            
        queue = asyncio.Queue()
        
        # Subscribe to direct topics
        for pattern in patterns:
            if '*' in pattern:
                self._patterns.append((pattern, queue))
            else:
                if pattern not in self._subscriptions:
                    self._subscriptions[pattern] = set()
                self._subscriptions[pattern].add(queue)
        
        try:
            while self._running:
                topic, message_dict = await queue.get()
                yield Message.from_dict(message_dict)
                queue.task_done()
        except asyncio.CancelledError:
            # Clean up on cancellation
            for pattern in patterns:
                if '*' in pattern:
                    self._patterns = [(p, q) for p, q in self._patterns 
                                    if p != pattern or q != queue]
                else:
                    if pattern in self._subscriptions:
                        self._subscriptions[pattern].discard(queue)
                        if not self._subscriptions[pattern]:
                            del self._subscriptions[pattern]
            raise
    
    async def request(self, topic: str, payload: Dict[str, Any] = None, 
                     timeout: float = 10.0, **kwargs) -> Message:
        """Send a request and wait for a response."""
        if not self._running:
            raise RuntimeError("Message bus is not running")
            
        message = Message(
            type=MessageType.INTENT,
            source="system",
            target=topic,
            payload=payload or {},
            **kwargs
        )
        
        response_queue = asyncio.Queue()
        response_pattern = f"response.{message.message_id}"
        
        # Subscribe to the response
        if response_pattern not in self._subscriptions:
            self._subscriptions[response_pattern] = set()
        self._subscriptions[response_pattern].add(response_queue)
        
        try:
            # Publish the request
            await self.publish(topic, message)
            
            # Wait for response with timeout
            try:
                _, response_dict = await asyncio.wait_for(
                    response_queue.get(),
                    timeout=timeout
                )
                return Message.from_dict(response_dict)
            except asyncio.TimeoutError:
                raise asyncio.TimeoutError(
                    f"Timeout waiting for response to {message.message_id}"
                )
        finally:
            # Clean up
            self._subscriptions[response_pattern].discard(response_queue)
            if not self._subscriptions[response_pattern]:
                del self._subscriptions[response_pattern]
    
    async def close(self):
        """Close the message bus and clean up resources."""
        self._running = False
        
        # Cancel all pending operations
        for queue in self._queues.values():
            while not queue.empty():
                queue.get_nowait()
                queue.task_done()
        
        # Clear subscriptions
        self._subscriptions.clear()
        self._patterns.clear()
    
    async def __aenter__(self):
        self._running = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
