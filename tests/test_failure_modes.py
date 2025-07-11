import pytest

from sios_messaging.inmemory import InMemoryBroker
from agent_core import AgentCore


def test_invalid_intent():
    broker = InMemoryBroker()
    # intentionally missing intent field
    broker.send_intent({"args": "foo"})
    core = AgentCore()
    for intent in broker.receive_intents():
        result = core.dispatch(intent)
        assert result["status"] == "error"
