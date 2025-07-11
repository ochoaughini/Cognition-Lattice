import asyncio
import time
import pytest

from agent_runtime_manager import AgentRuntimeManager


@pytest.mark.asyncio
async def test_run_with_backoff():
    rm = AgentRuntimeManager()

    async def failing():
        raise RuntimeError("boom")

    start = time.monotonic()
    with pytest.raises(RuntimeError):
        await rm.run_with_backoff('b', failing, retries=3, base_delay=0.1)
    elapsed = time.monotonic() - start
    assert elapsed >= 0.7
