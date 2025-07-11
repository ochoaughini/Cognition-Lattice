import asyncio
import shutil
import threading
import subprocess
import os
import sys
import types
import pytest

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
from agent_core import AgentCore
import sios_messaging as messaging


@pytest.mark.asyncio
async def test_broker_reconnect():
    if shutil.which('docker') is None:
        pytest.skip('docker not available')

    os.environ['MESSAGE_BROKER'] = 'redis'
    os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')

    core = AgentCore()
    t = threading.Thread(target=core.loop, daemon=True)
    t.start()
    try:
        messaging.send_intent({'intent': 'echo', 'args': 'a', 'intent_id': '1'})
        await asyncio.sleep(0.2)
        subprocess.run(['docker', 'restart', 'redis'], check=True)
        messaging.send_intent({'intent': 'echo', 'args': 'b', 'intent_id': '2'})
        await asyncio.sleep(0.5)
        responses = list(messaging.receive_responses())
        ids = {r.get('intent_id') for r in responses}
        assert {'1', '2'} <= ids
    finally:
        if hasattr(core, '_observer'):
            core._observer.stop()
            core._observer.join()
