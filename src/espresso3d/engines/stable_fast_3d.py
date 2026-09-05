"""Stable Fast 3D — balance of quality and weight, ships with UV and basic PBR."""

from __future__ import annotations

from ..config import PipelineConfig
from .base import EngineInfo, Engine, MissingDependency


class StableFast3D(Engine):
    info = EngineInfo(
        id="stable_fast_3d",
        name="Stable Fast 3D",
        description="Balanced · UV and basic PBR",
        vram_min_gb=6.0,
        weights_license="Stability AI Community License",
        # Stability's license allows personal use and companies with annual
        # revenue under US$1M. For "commercial use" without caveats, the app
        # suggests a different engine.
        commercial_use=False,
        pbr=True,
        repo="stabilityai/stable-fast-3d",
    )

    _model = None

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            from sf3d.system import SF3D  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on download
            raise MissingDependency(
                "sf3d (Stable Fast 3D)",
                "pip install git+https://github.com/Stability-AI/stable-fast-3d.git",
            ) from exc

        import torch

        model = SF3D.from_pretrained(
            self.info.repo, config_name="config.yaml", weight_name="model.safetensors"
        )
        model.to("cuda" if torch.cuda.is_available() else "cpu")
        model.eval()
        StableFast3D._model = model
        return model

    def _generate(self, image, cfg: PipelineConfig):  # pragma: no cover - needs a GPU
        import torch

        model = self._load()
        with torch.no_grad():
            mesh, _ = model.run_image(
                image,
                bake_resolution=cfg.texture_resolution.pixels,
                remesh="none",
            )
        return mesh
