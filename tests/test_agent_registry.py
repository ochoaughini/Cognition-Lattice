import importlib
from pathlib import Path

import agent_core


def _write_agent(path: Path, name: str, intent: str) -> None:
    path.write_text(
        'from cognition_lattice.base_agent import BaseAgent\n'
        f'class {name}(BaseAgent):\n'
        f'    intent_types = ["{intent}"]\n'
        '    def execute(self, intent):\n'
        '        return {"status": "ok"}\n'
    )


def test_dynamic_agent_registration(monkeypatch):
    agents_dir = Path('cognition_lattice/agents')
    a_file = agents_dir / 'tmp_agent_a.py'
    b_file = agents_dir / 'tmp_agent_b.py'
    _write_agent(a_file, 'TmpAgentA', 'a')
    _write_agent(b_file, 'TmpAgentB', 'b')

    monkeypatch.setattr(agent_core.AgentCore, '_start_watcher', lambda self: None)
    monkeypatch.setattr(agent_core, 'start_metrics_server', lambda port=8001: None)

    try:
        core = agent_core.AgentCore()
        assert 'a' in core.registry
        assert 'b' in core.registry

        b_file.unlink()
        importlib.invalidate_caches()
        core._load_agents()
        assert 'b' not in core.registry
    finally:
        if a_file.exists():
            a_file.unlink()
        if b_file.exists():
            b_file.unlink()
