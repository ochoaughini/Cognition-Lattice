"""
Resource management for compute and accelerator resources.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
import subprocess
import psutil
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of compute resources."""
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    OPENCL = "opencl"
    TPU = "tpu"
    RAY = "ray"
    DASK = "dask"


@dataclass
class Resource:
    """Represents a compute resource."""
    type: ResourceType
    id: str
    name: str
    capacity: float = 1.0
    available: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceAllocationError(Exception):
    """Raised when resource allocation fails."""


class ResourceManager:
    """Manages allocation and deallocation of compute resources."""

    def __init__(self) -> None:
        self.resources: Dict[Tuple[ResourceType, str], Resource] = {}
        self.executors: Dict[str, Union[ThreadPoolExecutor, ProcessPoolExecutor]] = {}
        self.loop = asyncio.get_event_loop()
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Detect available resources and initialize executors."""
        if self._initialized:
            return

        async with self._lock:
            await self._detect_cpu_resources()
            await self._detect_gpu_resources()
            self._init_executors()
            self._initialized = True
            logger.info("Resource manager initialized")

    async def _detect_cpu_resources(self) -> None:
        """Detect available CPU resources."""
        cpu_count = os.cpu_count() or 1
        freq = psutil.cpu_freq()
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False) or cpu_count,
            "logical_cores": cpu_count,
            "min_freq": freq.min if freq else 0,
            "max_freq": freq.max if freq else 0,
            "current_freq": freq.current if freq else 0,
        }
        cpu_resource = Resource(
            type=ResourceType.CPU,
            id="cpu:0",
            name="Main CPU",
            capacity=float(cpu_count),
            available=float(cpu_count),
            metadata={"cpu_info": cpu_info},
        )
        self.resources[(ResourceType.CPU, "cpu:0")] = cpu_resource
        logger.info("Detected CPU: %s logical cores", cpu_count)

    async def _detect_gpu_resources(self) -> None:
        """Detect available GPU resources."""
        try:
            nvidia_smi = await self._run_command("nvidia-smi -L")
            if nvidia_smi:
                for i, line in enumerate(nvidia_smi.strip().split("\n")):
                    gpu_name = line.split(":", 1)[1].split("(")[0].strip()
                    gpu_id = f"cuda:{i}"
                    mem_info = await self._get_gpu_memory(i)
                    gpu_resource = Resource(
                        type=ResourceType.CUDA,
                        id=gpu_id,
                        name=f"{gpu_name} (CUDA)",
                        capacity=1.0,
                        available=1.0,
                        metadata={
                            "name": gpu_name,
                            "memory": mem_info,
                            "driver_version": await self._get_nvidia_driver_version(),
                        },
                    )
                    self.resources[(ResourceType.CUDA, gpu_id)] = gpu_resource
                    logger.info("Detected GPU: %s (%s)", gpu_name, gpu_id)
        except (FileNotFoundError, subprocess.SubprocessError) as exc:
            logger.debug("NVIDIA GPU detection failed: %s", exc)
        # TODO: Add detection for ROCm and OpenCL devices

    async def _get_nvidia_driver_version(self) -> str:
        """Return NVIDIA driver version."""
        try:
            result = await self._run_command(
                "nvidia-smi --query-gpu=driver_version --format=csv,noheader"
            )
            return result.strip() if result else "unknown"
        except (FileNotFoundError, subprocess.SubprocessError):
            return "not available"

    async def _get_gpu_memory(self, gpu_id: int) -> Dict[str, float]:
        """Return GPU memory statistics."""
        try:
            result = await self._run_command(
                f"nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits --id={gpu_id}"
            )
            if result:
                total, used, free = map(float, result.strip().split(","))
                return {
                    "total_mb": total,
                    "used_mb": used,
                    "free_mb": free,
                    "utilization": (used / total) * 100 if total > 0 else 0,
                }
        except (ValueError, subprocess.SubprocessError) as exc:
            logger.warning("Failed to get GPU memory info: %s", exc)
        return {"total_mb": 0, "used_mb": 0, "free_mb": 0, "utilization": 0}

    async def _run_command(self, command: str) -> str:
        """Run shell command and return its output."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
        return stdout.decode("utf-8").strip()

    def _init_executors(self) -> None:
        """Initialize thread and process executors."""
        self.executors["io"] = ThreadPoolExecutor(
            max_workers=min(32, (os.cpu_count() or 1) * 5), thread_name_prefix="io_worker"
        )
        self.executors["cpu"] = ProcessPoolExecutor(max_workers=os.cpu_count() or 1)

    async def allocate(
        self,
        resource_type: ResourceType,
        amount: float = 1.0,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> List[Resource]:
        """Allocate resources of the given type."""
        await self.initialize()
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        async with self._lock:
            matching = [
                r
                for (t, _), r in self.resources.items()
                if t == resource_type and r.available >= amount
            ]
            if not matching:
                raise ResourceAllocationError(
                    f"No available {resource_type.value} resources with {amount} capacity"
                )
            matching.sort(key=lambda r: r.available, reverse=True)
            resource = matching[0]
            allocated = min(amount, resource.available)
            resource.available -= allocated
            allocated_resource = Resource(
                type=resource.type,
                id=f"{resource.id}:{id(allocated):x}",
                name=f"{resource.name} (allocated)",
                capacity=allocated,
                available=allocated,
                metadata=resource.metadata.copy(),
            )
            logger.debug(
                "Allocated %s of %s (remaining: %.2f)",
                allocated,
                resource.name,
                resource.available,
            )
            return [allocated_resource]

    async def release(self, resources: List[Resource]) -> None:
        """Release previously allocated resources."""
        if not resources:
            return
        async with self._lock:
            for resource in resources:
                base_id = resource.id.split(":", 1)[0]
                for (rtype, rid), base_resource in self.resources.items():
                    if rtype == resource.type and rid.startswith(base_id):
                        base_resource.available = min(
                            base_resource.available + resource.capacity,
                            base_resource.capacity,
                        )
                        logger.debug(
                            "Released %s of %s (available: %.2f)",
                            resource.capacity,
                            base_resource.name,
                            base_resource.available,
                        )
                        break

    async def get_executor(
        self, executor_type: str = "io"
    ) -> Union[ThreadPoolExecutor, ProcessPoolExecutor]:
        """Return an executor for running tasks."""
        if executor_type not in self.executors:
            raise ValueError(f"Unknown executor type: {executor_type}")
        return self.executors[executor_type]

    async def cleanup(self) -> None:
        """Shutdown executors and clear resources."""
        for name, executor in self.executors.items():
            logger.debug("Shutting down %s executor", name)
            executor.shutdown(wait=False)
        self.executors.clear()
        self.resources.clear()
        self._initialized = False

    async def get_resource_usage(self) -> Dict[str, Any]:
        """Return current resource usage statistics."""
        await self.initialize()
        usage: Dict[str, Any] = {
            "cpu": {
                "usage_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
            },
            "gpu": [],
            "executors": {},
        }
        for (rtype, rid), resource in self.resources.items():
            if rtype == ResourceType.CUDA:
                usage["gpu"].append(
                    {
                        "id": rid,
                        "name": resource.name,
                        "utilization": resource.metadata.get("memory", {}).get(
                            "utilization", 0
                        ),
                        "memory_used_mb": resource.metadata.get("memory", {}).get(
                            "used_mb", 0
                        ),
                        "memory_total_mb": resource.metadata.get("memory", {}).get(
                            "total_mb", 0
                        ),
                        "allocated": 1.0 - resource.available,
                    }
                )
        for name, executor in self.executors.items():
            if isinstance(executor, ThreadPoolExecutor):
                usage["executors"][name] = {
                    "type": "thread",
                    "max_workers": executor._max_workers,
                    "active_threads": len([t for t in executor._threads if t.is_alive()]),
                }
            elif isinstance(executor, ProcessPoolExecutor):
                usage["executors"][name] = {
                    "type": "process",
                    "max_workers": executor._max_workers,
                    "processes": len(executor._processes)
                    if hasattr(executor, "_processes")
                    else 0,
                }
        return usage

    async def __aenter__(self) -> "ResourceManager":
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.cleanup()
