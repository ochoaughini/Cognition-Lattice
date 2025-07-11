import yaml
from pathlib import Path

from multi_agent_harmonizer import MultiAgentHarmonizer
from cognition_lattice.agents.plan_agent import PlanAgent
from cognition_lattice.agents.act_agent import ActAgent
from cognition_lattice.agents.verify_agent import VerifyAgent


def test_workflow_saga():
    workflow_file = Path('tests/fixtures/workflows/test_plan_act_verify.yaml')
    steps = yaml.safe_load(workflow_file.read_text())

    plan = PlanAgent()
    act = ActAgent()
    verify = VerifyAgent()

    harmonizer = MultiAgentHarmonizer([plan, act, verify])
    results = harmonizer.run_all({"workflow": steps})

    assert results[-1]["status"] == "error"
    assert plan.rolled_back
    assert act.rolled_back
