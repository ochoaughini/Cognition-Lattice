import asyncio
import pytest
import sys
import types
from agent_runtime_manager import AgentRuntimeManager
psutil = pytest.importorskip('psutil')
from pathlib import Path

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
async def test_run_with_timeout():
    rm = AgentRuntimeManager()
    async def long_task():
        await asyncio.sleep(1)
    with pytest.raises(asyncio.TimeoutError):
        await rm.run_with_timeout('t', long_task(), timeout=0.1)
    assert 't' not in rm.tasks


@pytest.mark.asyncio
async def test_run_with_timeout_dynamic_agent(tmp_path, monkeypatch):
    agents_dir = Path('cognition_lattice/agents')
    agent_file = agents_dir / 'tmp_timeout_agent.py'
    agent_file.write_text(
        'import asyncio\n'
        'from cognition_lattice.base_agent import BaseAgent\n'
        'class TmpTimeoutAgent(BaseAgent):\n'
        '    intent_types = ["timeout"]\n'
        '    async def execute(self, intent):\n'
        '        while True:\n'
        '            await asyncio.sleep(0.1)\n'
    )

    monkeypatch.setattr(agent_core.AgentCore, '_start_watcher', lambda self: None)
    monkeypatch.setattr(agent_core, 'start_metrics_server', lambda port=8001: None)

    log_path = tmp_path / 'runtime.log'
    import logging
    handler = logging.FileHandler(str(log_path))
    logger = logging.getLogger('agent_runtime_manager')
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    rm = AgentRuntimeManager()
    core = agent_core.AgentCore()
    agent_cls = core.registry['timeout']
    agent = agent_cls()

    intent = {'intent': 'timeout', 'intent_id': '123'}
    proc = psutil.Process()
    fds_before = proc.num_fds()

    with pytest.raises(asyncio.TimeoutError):
        await rm.run_with_timeout(intent['intent_id'], agent.execute(intent), timeout=0.1)

    assert intent['intent_id'] not in rm.tasks
    assert proc.num_fds() <= fds_before + 1

    import logging
    logging.shutdown()
    log_content = Path(log_path).read_text()
    assert 'timed out' in log_content and intent['intent_id'] in log_content

    agent_file.unlink()
    pycache = agent_file.parent / '__pycache__'
    if pycache.exists():
        for f in pycache.iterdir():
            if f.name.startswith('tmp_timeout_agent'):
                f.unlink()
