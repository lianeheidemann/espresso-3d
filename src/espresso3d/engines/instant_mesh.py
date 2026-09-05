"""InstantMesh — maximum quality of the trio, via multi-view diffusion."""

from __future__ import annotations

from ..config import PipelineConfig
from .base import EngineInfo, Engine, MissingDependency


class InstantMesh(Engine):
    info = EngineInfo(
        id="instant_mesh",
        name="InstantMesh",
        description="Maximum quality · multi-view",
        vram_min_gb=8.0,
        weights_license="Apache 2.0",
        commercial_use=True,
        pbr=True,
        repo="TencentARC/InstantMesh",
    )

    _pipeline = None

    def _load(self):
        if self._pipeline is not None:
            return self._pipeline
        try:
            import instantmesh  # type: ignore  # noqa: F401
        except ImportError as exc:  # pragma: no cover - depends on download
            raise MissingDependency(
                "instantmesh",
                "git clone https://github.com/TencentARC/InstantMesh "
                "&& pip install -r InstantMesh/requirements.txt",
            ) from exc

        from instantmesh.pipeline import InstantMeshPipeline  # type: ignore

        InstantMesh._pipeline = InstantMeshPipeline.from_pretrained(self.info.repo)
        return InstantMesh._pipeline

    def _generate(self, image, cfg: PipelineConfig):  # pragma: no cover - needs a GPU
        pipeline = self._load()
        return pipeline(
            image,
            texture=cfg.generate_texture,
            texture_resolution=cfg.texture_resolution.pixels,
        )
