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

    async def run_with_retry(
        self,
        name: str,
        func,
        retries: int = 3,
        delay: float = 0.1,
    ):
        for attempt in range(1, retries + 1):
            task = asyncio.create_task(func())
            self.tasks[name] = task
            try:
                result = await task
                self.tasks.pop(name, None)
                return result
            except Exception as exc:
                self.logger.warning(
                    "Task %s failed attempt %d: %s", name, attempt, exc
                )
                self.tasks.pop(name, None)
                if attempt == retries:
                    self.logger.warning(
                        "Task %s giving up after %d attempts", name, retries
                    )
                    raise
                await asyncio.sleep(delay)
