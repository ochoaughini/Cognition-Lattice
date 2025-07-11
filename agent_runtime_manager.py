"""Track active agent tasks with timeouts."""

import asyncio
import logging
from typing import Dict


class AgentRuntimeManager:
    def __init__(self) -> None:
        self.tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)

    async def run_with_timeout(self, name: str, coro, timeout: float) -> None:
        task = asyncio.create_task(coro)
        self.tasks[name] = task
        try:
            await asyncio.wait_for(task, timeout)
        except asyncio.TimeoutError:
            self.logger.warning("Task %s timed out after %.2fs", name, timeout)
            raise
        finally:
            self.tasks.pop(name, None)
