"""Track active agent tasks with timeouts."""

import asyncio
from typing import Dict


class AgentRuntimeManager:
    def __init__(self) -> None:
        self.tasks: Dict[str, asyncio.Task] = {}

    async def run_with_timeout(self, name: str, coro, timeout: float) -> None:
        task = asyncio.create_task(coro)
        self.tasks[name] = task
        try:
            await asyncio.wait_for(task, timeout)
        finally:
            self.tasks.pop(name, None)
