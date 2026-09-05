"""Common interface for the 3D generation engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..config import License, PipelineConfig


class MissingDependency(RuntimeError):
    """Error with installation instructions, instead of a bare ImportError."""

    def __init__(self, package: str, how_to_install: str):
        super().__init__(
            f"'{package}' is not installed.\n\nTo install:\n  {how_to_install}"
        )
        self.package = package
        self.how_to_install = how_to_install


@dataclass(frozen=True)
class EngineInfo:
    """Metadata the UI shows before the engine is loaded."""

    id: str
    name: str
    description: str
    vram_min_gb: float
    weights_license: str
    commercial_use: bool
    pbr: bool
    repo: str


class Engine(ABC):
    """A 3D mesh generator from an image.

    The weights are heavy (GB) and the dependencies are specific to each
    project, so everything is imported only at generation time — that way
    the app opens normally on a machine with nothing installed and explains
    what's missing.
    """

    info: EngineInfo

    @abstractmethod
    def _generate(self, image, cfg: PipelineConfig):
        """Returns a ``trimesh.Trimesh``. Implemented by each engine."""

    def generate(self, image, cfg: PipelineConfig):
        free_vram = _vram()
        if free_vram is not None and free_vram + 0.5 < self.info.vram_min_gb:
            raise RuntimeError(
                f"{self.info.name} needs ~{self.info.vram_min_gb:g} GB of VRAM "
                f"and your GPU has {free_vram:g} GB. "
                "Choose a lighter engine from the list."
            )
        return self._generate(image, cfg)

    def compatible_with(self, license: License) -> bool:
        if license is License.COMMERCIAL:
            return self.info.commercial_use
        return True

    def __repr__(self) -> str:  # pragma: no cover - debug convenience
        return f"<Engine {self.info.id}>"


def _vram() -> float | None:
    from ..hardware import vram_gb

    return vram_gb()
