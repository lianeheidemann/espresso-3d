"""Registry of the 3D generation engines.

Adding a new engine means creating the module and adding a line to
:data:`ENGINES` — the UI updates itself automatically from there.
"""

from __future__ import annotations

from ..config import License
from .base import EngineInfo, Engine, MissingDependency
from .instant_mesh import InstantMesh
from .stable_fast_3d import StableFast3D
from .tripo_sr import TripoSR

ENGINES: dict[str, Engine] = {
    m.info.id: m
    for m in (TripoSR(), StableFast3D(), InstantMesh())
}

__all__ = [
    "ENGINES",
    "Engine",
    "EngineInfo",
    "MissingDependency",
    "get",
    "list_engines",
    "suggest",
]


def get(engine_id: str) -> Engine:
    if engine_id not in ENGINES:
        known = ", ".join(ENGINES)
        raise KeyError(f"Engine '{engine_id}' doesn't exist. Available: {known}")
    return ENGINES[engine_id]


def list_engines(license: License | None = None, vram_gb: float | None = None) -> list[Engine]:
    """Engines compatible with the requested license and the machine's GPU."""
    engines = list(ENGINES.values())
    if license is not None:
        engines = [m for m in engines if m.compatible_with(license)]
    if vram_gb is not None:
        engines = [m for m in engines if m.info.vram_min_gb <= vram_gb + 0.5]
    return engines


def suggest(vram_gb: float | None = None, license: License | None = None) -> Engine:
    """The best engine that fits the available GPU.

    With no GPU detected, returns the lightest one: it's the only one that
    runs on CPU in a tolerable time.
    """
    candidates = list_engines(license=license, vram_gb=vram_gb)
    if not candidates:
        return get("tripo_sr")
    return max(candidates, key=lambda m: m.info.vram_min_gb)
