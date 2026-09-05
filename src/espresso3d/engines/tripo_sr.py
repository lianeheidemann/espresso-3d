"""TripoSR — the lightest engine, runs even on a 4GB GPU."""

from __future__ import annotations

from ..config import PipelineConfig
from .base import EngineInfo, Engine, MissingDependency


class TripoSR(Engine):
    info = EngineInfo(
        id="tripo_sr",
        name="TripoSR",
        description="Fast · ~5s per image",
        vram_min_gb=4.0,
        weights_license="MIT",
        commercial_use=True,
        pbr=False,
        repo="stabilityai/TripoSR",
    )

    _model = None

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            from tsr.system import TSR  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on download
            raise MissingDependency(
                "tsr (TripoSR)",
                "pip install git+https://github.com/VAST-AI-Research/TripoSR.git",
            ) from exc

        import torch

        model = TSR.from_pretrained(
            self.info.repo,
            config_name="config.yaml",
            weight_name="model.ckpt",
        )
        model.renderer.set_chunk_size(8192)
        model.to("cuda" if torch.cuda.is_available() else "cpu")
        TripoSR._model = model
        return model

    def _generate(self, image, cfg: PipelineConfig):  # pragma: no cover - needs a GPU
        import torch

        model = self._load()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        with torch.no_grad():
            codes = model([image], device=device)
            meshes = model.extract_mesh(codes, has_vertex_color=cfg.generate_texture)
        return meshes[0]
