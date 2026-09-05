"""InstantMesh — qualidade máxima do trio, via difusão multi-view."""

from __future__ import annotations

from ..config import PipelineConfig
from .base import DependenciaFaltando, InfoMotor, Motor


class InstantMesh(Motor):
    info = InfoMotor(
        id="instant_mesh",
        nome="InstantMesh",
        descricao="Máxima qualidade · multi-view",
        vram_min_gb=8.0,
        licenca_pesos="Apache 2.0",
        uso_comercial=True,
        pbr=True,
        repo="TencentARC/InstantMesh",
    )

    _pipe = None

    def _carregar(self):
        if self._pipe is not None:
            return self._pipe
        try:
            import instantmesh  # type: ignore  # noqa: F401
        except ImportError as exc:  # pragma: no cover - depende de download
            raise DependenciaFaltando(
                "instantmesh",
                "git clone https://github.com/TencentARC/InstantMesh "
                "&& pip install -r InstantMesh/requirements.txt",
            ) from exc

        from instantmesh.pipeline import InstantMeshPipeline  # type: ignore

        InstantMesh._pipe = InstantMeshPipeline.from_pretrained(self.info.repo)
        return InstantMesh._pipe

    def _gerar(self, imagem, cfg: PipelineConfig):  # pragma: no cover - precisa de GPU
        pipe = self._carregar()
        return pipe(
            imagem,
            texture=cfg.gerar_textura,
            texture_resolution=cfg.resolucao_textura.pixels,
        )
