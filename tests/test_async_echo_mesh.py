import json
import pytest
from pathlib import Path
import asyncio

from agent_core import AgentMesh


@pytest.mark.asyncio
async def test_async_echo_agent(tmp_path):
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    manifest = {
        "id": "echo_agent",
        "module": "async_echo_agent",
        "function": "echo_agent",
        "subscriptions": ["echo.*"],
    }
    Path(manifest_dir / "echo_agent.json").write_text(json.dumps(manifest))

    mesh = AgentMesh(str(manifest_dir))
    await mesh.start()
    await asyncio.sleep(0.05)
    try:
        response = await mesh.message_bus.request("echo.test", {"message": "hi"})
        assert response.payload["original_payload"]["message"] == "hi"
    finally:
        await mesh.stop()

