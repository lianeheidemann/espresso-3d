"""TripoSR — o motor mais leve, roda até em GPU de 4GB."""

from __future__ import annotations

from ..config import PipelineConfig
from .base import DependenciaFaltando, InfoMotor, Motor


class TripoSR(Motor):
    info = InfoMotor(
        id="tripo_sr",
        nome="TripoSR",
        descricao="Rápido · ~5s por imagem",
        vram_min_gb=4.0,
        licenca_pesos="MIT",
        uso_comercial=True,
        pbr=False,
        repo="stabilityai/TripoSR",
    )

    _modelo = None

    def _carregar(self):
        if self._modelo is not None:
            return self._modelo
        try:
            from tsr.system import TSR  # type: ignore
        except ImportError as exc:  # pragma: no cover - depende de download
            raise DependenciaFaltando(
                "tsr (TripoSR)",
                "pip install git+https://github.com/VAST-AI-Research/TripoSR.git",
            ) from exc

        import torch

        modelo = TSR.from_pretrained(
            self.info.repo,
            config_name="config.yaml",
            weight_name="model.ckpt",
        )
        modelo.renderer.set_chunk_size(8192)
        modelo.to("cuda" if torch.cuda.is_available() else "cpu")
        TripoSR._modelo = modelo
        return modelo

    def _gerar(self, imagem, cfg: PipelineConfig):  # pragma: no cover - precisa de GPU
        import torch

        modelo = self._carregar()
        dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        with torch.no_grad():
            codigos = modelo([imagem], device=dispositivo)
            malhas = modelo.extract_mesh(codigos, has_vertex_color=cfg.gerar_textura)
        return malhas[0]
