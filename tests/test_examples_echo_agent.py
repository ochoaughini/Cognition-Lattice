import json
import asyncio
from pathlib import Path
import pytest
from agent_core import AgentMesh


@pytest.mark.asyncio
async def test_examples_echo_agent(tmp_path):
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    manifest = {
        "id": "examples_echo_agent",
        "module": "examples.echo_agent",
        "function": "echo_agent",
        "subscriptions": ["echo.*"],
    }
    Path(manifest_dir / "examples_echo_agent.json").write_text(json.dumps(manifest))

    mesh = AgentMesh(str(manifest_dir))
    await mesh.start()
    await asyncio.sleep(0.05)
    try:
        response = await mesh.message_bus.request("echo.test", {"data": "hello"})
        assert response.payload["original_payload"]["data"] == "hello"
    finally:
        await mesh.stop()
