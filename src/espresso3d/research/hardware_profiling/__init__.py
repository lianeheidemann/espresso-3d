"""Hardware and execution profiling for experiments."""

from dataclasses import dataclass

from ...hardware import gpu_name, vram_gb


@dataclass(frozen=True)
class HardwareSnapshot:
    gpu: str | None
    vram_gb: float | None


def snapshot() -> HardwareSnapshot:
    return HardwareSnapshot(gpu=gpu_name(), vram_gb=vram_gb())
