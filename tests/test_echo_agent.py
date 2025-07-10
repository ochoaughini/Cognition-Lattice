from cognition_lattice.agents.echo_agent import EchoAgent


def test_echo_agent():
    agent = EchoAgent()
    intent = {"intent": "echo", "args": "hi", "intent_id": "123"}
    result = agent.execute(intent)
    assert result["status"] == "ok"
    assert result["echo"] == "hi"
