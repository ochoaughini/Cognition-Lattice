import asyncio
import pytest

from resource_manager import ResourceManager, ResourceType


@pytest.mark.asyncio
async def test_allocate_release_cpu():
    rm = ResourceManager()
    resources = await rm.allocate(ResourceType.CPU, 1.0)
    assert resources
    base = rm.resources[(ResourceType.CPU, "cpu:0")]
    assert base.available == base.capacity - 1.0
    await rm.release(resources)
    assert base.available == base.capacity
    await rm.cleanup()
