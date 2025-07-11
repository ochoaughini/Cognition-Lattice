from multi_agent_harmonizer import MultiAgentHarmonizer
from cognition_lattice.base_agent import BaseAgent

class OkAgent(BaseAgent):
    def __init__(self):
        self.executed = False
        self.rolled_back = False
    def execute(self, intent):
        self.executed = True
        return {"status": "ok"}
    def rollback(self, intent):
        self.rolled_back = True

class FailAgent(BaseAgent):
    def execute(self, intent):
        return {"status": "error", "message": "fail"}


def test_harmonizer_rollback():
    a1 = OkAgent()
    a2 = FailAgent()
    a3 = OkAgent()
    harmonizer = MultiAgentHarmonizer([a1, a2, a3])
    results = harmonizer.run_all({"intent": "test"})
    assert results[-1]["status"] == "error"
    assert a1.executed and a1.rolled_back
    assert not a3.executed

