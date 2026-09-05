"""Stable Fast 3D — equilíbrio entre qualidade e peso, já sai com UV e PBR básico."""

from __future__ import annotations

from ..config import PipelineConfig
from .base import DependenciaFaltando, InfoMotor, Motor


class StableFast3D(Motor):
    info = InfoMotor(
        id="stable_fast_3d",
        nome="Stable Fast 3D",
        descricao="Equilíbrio · UV e PBR básico",
        vram_min_gb=6.0,
        licenca_pesos="Stability AI Community License",
        # A licença da Stability permite uso pessoal e empresas com receita
        # anual abaixo de US$1M. Para "uso comercial" sem ressalva, o app
        # sugere outro motor.
        uso_comercial=False,
        pbr=True,
        repo="stabilityai/stable-fast-3d",
    )

    _modelo = None

    def _carregar(self):
        if self._modelo is not None:
            return self._modelo
        try:
            from sf3d.system import SF3D  # type: ignore
        except ImportError as exc:  # pragma: no cover - depende de download
            raise DependenciaFaltando(
                "sf3d (Stable Fast 3D)",
                "pip install git+https://github.com/Stability-AI/stable-fast-3d.git",
            ) from exc

        import torch

        modelo = SF3D.from_pretrained(
            self.info.repo, config_name="config.yaml", weight_name="model.safetensors"
        )
        modelo.to("cuda" if torch.cuda.is_available() else "cpu")
        modelo.eval()
        StableFast3D._modelo = modelo
        return modelo

    def _gerar(self, imagem, cfg: PipelineConfig):  # pragma: no cover - precisa de GPU
        import torch

        modelo = self._carregar()
        with torch.no_grad():
            malha, _ = modelo.run_image(
                imagem,
                bake_resolution=cfg.resolucao_textura.pixels,
                remesh="none",
            )
        return malha
