"""Divisão em partes: separa os objetos da imagem ANTES de gerar o 3D.

O truque: em vez de tentar cortar uma malha 3D já fundida (difícil e
propenso a erro), separamos na imagem 2D com o Segment Anything e geramos
um modelo por recorte. A xícara e o pires nascem como dois objetos
independentes, em vez de virarem um sólido só.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

#: Máscaras menores que isso (fração da imagem) são ruído, não objeto.
_AREA_MINIMA = 0.02
#: Mais que isso vira uma fila de geração longa demais para valer a pena.
_MAX_PARTES = 6


class SamIndisponivel(RuntimeError):
    def __init__(self):
        super().__init__(
            "Para dividir em partes é preciso o Segment Anything:\n"
            "  pip install segment-anything\n"
            "e baixar o checkpoint 'vit_b' (~360MB) para checkpoints/sam_vit_b.pth"
        )


def separar_objetos(imagem, max_partes: int = _MAX_PARTES) -> list:
    """Devolve um recorte RGBA por objeto encontrado.

    Sem o SAM instalado, devolve a imagem inteira como parte única — o
    app segue funcionando, só sem a divisão.
    """
    try:
        mascaras = _mascaras_sam(imagem)
    except Exception as exc:
        log.info("SAM indisponível (%s) — gerando o objeto inteiro.", exc)
        return [imagem]

    if not mascaras:
        return [imagem]

    return [_recortar(imagem, m) for m in mascaras[:max_partes]]


def _mascaras_sam(imagem) -> list:  # pragma: no cover - precisa de checkpoint
    from pathlib import Path

    import numpy as np
    from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

    checkpoint = Path("checkpoints/sam_vit_b.pth")
    if not checkpoint.exists():
        raise SamIndisponivel()

    import torch

    sam = sam_model_registry["vit_b"](checkpoint=str(checkpoint))
    sam.to("cuda" if torch.cuda.is_available() else "cpu")

    gerador = SamAutomaticMaskGenerator(sam, points_per_side=16)
    achadas = gerador.generate(np.array(imagem.convert("RGB")))

    total = imagem.size[0] * imagem.size[1]
    grandes = [m for m in achadas if m["area"] / total >= _AREA_MINIMA]
    grandes.sort(key=lambda m: m["area"], reverse=True)
    return [m["segmentation"] for m in grandes]


def _recortar(imagem, mascara):  # pragma: no cover - só roda com SAM
    import numpy as np
    from PIL import Image

    rgba = np.array(imagem.convert("RGBA"))
    rgba[..., 3] = np.where(mascara, 255, 0)

    ys, xs = np.where(mascara)
    if not len(ys):
        return imagem
    caixa = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    return Image.fromarray(rgba).crop(caixa)
