import asyncio
import pytest

from agent_core import AgentCore
import sios_messaging as messaging


@pytest.mark.asyncio
async def test_full_pipeline():
    core = AgentCore()
    messaging.send_intent({"intent": "echo", "args": "hi", "intent_id": "1"})
    await asyncio.sleep(0.2)
    for resp in messaging.receive_responses(timeout=1.0):
        assert resp["intent_id"] == "1"
        break
