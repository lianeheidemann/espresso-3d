"""Splitting into parts: separates the objects in the image BEFORE generating the 3D.

The trick: instead of trying to cut an already-fused 3D mesh (hard and
error-prone), we separate in the 2D image with Segment Anything and
generate one model per crop. The cup and the saucer are born as two
independent objects, instead of turning into a single solid.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

#: Masks smaller than this (fraction of the image) are noise, not an object.
_MIN_AREA = 0.02
#: More than this turns into a generation queue too long to be worth it.
_MAX_PARTS = 6


class SamUnavailable(RuntimeError):
    def __init__(self):
        super().__init__(
            "To split into parts you need Segment Anything:\n"
            "  pip install segment-anything\n"
            "and download the 'vit_b' checkpoint (~360MB) to checkpoints/sam_vit_b.pth"
        )


def separate_objects(image, max_parts: int = _MAX_PARTS) -> list:
    """Returns one RGBA crop per object found.

    Without SAM installed, returns the whole image as a single part —
    the app keeps working, just without the splitting.
    """
    try:
        masks = _sam_masks(image)
    except Exception as exc:
        log.info("SAM unavailable (%s) — generating the whole object.", exc)
        return [image]

    if not masks:
        return [image]

    return [_crop(image, m) for m in masks[:max_parts]]


def _sam_masks(image) -> list:  # pragma: no cover - needs a checkpoint
    from pathlib import Path

    import numpy as np
    from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

    checkpoint = Path("checkpoints/sam_vit_b.pth")
    if not checkpoint.exists():
        raise SamUnavailable()

    import torch

    sam = sam_model_registry["vit_b"](checkpoint=str(checkpoint))
    sam.to("cuda" if torch.cuda.is_available() else "cpu")

    generator = SamAutomaticMaskGenerator(sam, points_per_side=16)
    found = generator.generate(np.array(image.convert("RGB")))

    total = image.size[0] * image.size[1]
    large = [m for m in found if m["area"] / total >= _MIN_AREA]
    large.sort(key=lambda m: m["area"], reverse=True)
    return [m["segmentation"] for m in large]


def _crop(image, mask):  # pragma: no cover - only runs with SAM
    import numpy as np
    from PIL import Image

    rgba = np.array(image.convert("RGBA"))
    rgba[..., 3] = np.where(mask, 255, 0)

    ys, xs = np.where(mask)
    if not len(ys):
        return image
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    return Image.fromarray(rgba).crop(box)
