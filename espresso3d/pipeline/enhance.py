"""Melhoria da imagem antes da geração 3D (Real-ESRGAN)."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

#: Acima disso não vale a pena melhorar — o motor 3D reduz a imagem mesmo.
_LADO_MAXIMO = 1024


def melhorar(imagem, escala: int = 2):
    """Aumenta e limpa a imagem. Devolve a original se o upscaler faltar.

    Falhar aqui não pode impedir a geração: imagem melhorada é um extra,
    não um requisito.
    """
    largura, altura = imagem.size
    if max(largura, altura) >= _LADO_MAXIMO:
        return imagem

    try:
        return _real_esrgan(imagem, escala)
    except Exception as exc:
        log.info("Real-ESRGAN indisponível (%s) — seguindo com a imagem original.", exc)
        return _reamostrar(imagem, escala)


def _real_esrgan(imagem, escala: int):  # pragma: no cover - precisa de download
    import numpy as np
    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    modelo = RRDBNet(
        num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4
    )
    upsampler = RealESRGANer(
        scale=4,
        model_path=(
            "https://github.com/xinntao/Real-ESRGAN/releases/download/"
            "v0.1.0/RealESRGAN_x4plus.pth"
        ),
        model=modelo,
        half=torch.cuda.is_available(),
    )
    saida, _ = upsampler.enhance(np.array(imagem.convert("RGB")), outscale=escala)

    from PIL import Image

    return Image.fromarray(saida)


def _reamostrar(imagem, escala: int):
    """Plano B honesto: reamostragem Lanczos, sem IA nenhuma."""
    from PIL import Image

    largura, altura = imagem.size
    novo = (min(largura * escala, _LADO_MAXIMO), min(altura * escala, _LADO_MAXIMO))
    return imagem.resize(novo, Image.LANCZOS)
