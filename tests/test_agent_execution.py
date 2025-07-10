from cognition_lattice.agents.echo_agent import EchoAgent


def test_echo_agent_execute():
    agent = EchoAgent()
    intent = {"intent": "echo", "args": "hi", "intent_id": "1"}
    result = agent.execute(intent)
    assert result == {"status": "ok", "echo": "hi"}
