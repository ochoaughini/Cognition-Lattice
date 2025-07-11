import asyncio
import logging
import sys
import types
from pathlib import Path

import pytest

from agent_runtime_manager import AgentRuntimeManager

psutil = pytest.importorskip('psutil')

if 'watchdog.observers' not in sys.modules:
    watchdog = types.ModuleType('watchdog')
    observers = types.ModuleType('watchdog.observers')
    events = types.ModuleType('watchdog.events')
    observers.Observer = object
    events.FileSystemEventHandler = object
    sys.modules['watchdog'] = watchdog
    sys.modules['watchdog.observers'] = observers
    sys.modules['watchdog.events'] = events

import agent_core


@pytest.mark.asyncio
async def test_run_with_retry_exhaustion(tmp_path, monkeypatch):
    agents_dir = Path('cognition_lattice/agents')
    agent_file = agents_dir / 'tmp_retry_agent.py'
    agent_file.write_text(
        'import asyncio\n'
        'from cognition_lattice.base_agent import BaseAgent\n'
        'class TmpRetryAgent(BaseAgent):\n'
        '    intent_types = ["retry"]\n'
        '    async def execute(self, intent):\n'
        '        raise RuntimeError("Intent failed")\n'
    )

    monkeypatch.setattr(agent_core.AgentCore, '_start_watcher', lambda self: None)
    monkeypatch.setattr(agent_core, 'start_metrics_server', lambda port=8001: None)

    log_path = tmp_path / 'retry.log'
    handler = logging.FileHandler(str(log_path))
    logger = logging.getLogger('agent_runtime_manager')
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    rm = AgentRuntimeManager()
    core = agent_core.AgentCore()
    agent_cls = core.registry['retry']
    agent = agent_cls()
    intent = {'intent': 'retry', 'intent_id': 'retry123'}

    with pytest.raises(RuntimeError):
        await rm.run_with_retry(intent['intent_id'], lambda: agent.execute(intent), retries=3, delay=0.1)

    log_output = Path(log_path).read_text()
    assert 'retry123' in log_output
    assert 'failed attempt 1' in log_output
    assert 'failed attempt 2' in log_output
    assert 'failed attempt 3' in log_output
    assert 'giving up' in log_output or 'exceeded retry limit' in log_output

    assert intent['intent_id'] not in rm.tasks

    agent_file.unlink()
    pycache = agent_file.parent / '__pycache__'
    if pycache.exists():
        for f in pycache.iterdir():
            if f.name.startswith('tmp_retry_agent'):
                f.unlink()

    logging.shutdown()
