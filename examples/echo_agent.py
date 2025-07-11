"""Example echo agent using numpy and pandas."""
import logging
from typing import Optional
import numpy as np
import pandas as pd
from agent_core import AgentContext
from messaging_bus import Message, MessageType

logger = logging.getLogger(__name__)

async def echo_agent(message: Message, context: AgentContext) -> Optional[Message]:
    """Echo the payload of intent messages."""
    logger.info(f"Echo agent received message: {message}")

    if message.type != MessageType.INTENT:
        return None

    # Demonstrate use of numpy and pandas
    arr = np.array([1, 2, 3])
    df = pd.DataFrame({"value": arr})

    response = message.reply({
        "original_payload": message.payload,
        "sum": int(df["value"].sum()),
        "processed_by": "examples.echo_agent",
        "timestamp": message.timestamp,
    })

    logger.info(f"Echo agent sending response: {response}")
    return response
