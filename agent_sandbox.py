"""Run agents in subprocesses for isolation."""

import asyncio
import json
import subprocess
from typing import Dict, Any


async def run_agent_subprocess(module: str, intent: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
    proc = await asyncio.create_subprocess_exec(
        "python", "-m", module,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout, _ = await proc.communicate(json.dumps(intent).encode())
    if stdout:
        return json.loads(stdout)
    return {"status": "error", "message": "no output"}
