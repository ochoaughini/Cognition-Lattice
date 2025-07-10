"""
Example echo agent that responds to messages.
"""
import asyncio
import logging
from typing import Dict, Any, Optional

from agent_core import AgentContext
from messaging_bus import Message, MessageType

logger = logging.getLogger(__name__)

async def echo_agent(message: Message, context: AgentContext) -> Optional[Message]:
    """
    Simple echo agent that responds to messages.
    
    Args:
        message: Incoming message
        context: Agent context
        
    Returns:
        Response message or None
    """
    logger.info(f"Echo agent received message: {message}")
    
    # Only respond to intent messages
    if message.type != MessageType.INTENT:
        return None
    
    # Create a response with the same payload
    response = message.reply({
        "original_payload": message.payload,
        "processed_by": "echo_agent",
        "timestamp": message.timestamp
    })
    
    logger.info(f"Echo agent sending response: {response}")
    return response
