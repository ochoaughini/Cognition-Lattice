import inspect
from importlib import import_module
from pathlib import Path
from cognition_lattice.base_agent import BaseAgent


def test_agents_implement_execute():
    agents_dir = Path('cognition_lattice/agents')
    for path in agents_dir.glob('*.py'):
        if path.name == '__init__.py':
            continue
        module = import_module(f'cognition_lattice.agents.{path.stem}')
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                assert not inspect.isabstract(obj), f"{name} is abstract"
                assert 'execute' in obj.__dict__, f"{name} missing execute"
