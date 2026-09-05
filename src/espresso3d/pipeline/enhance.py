"""Image enhancement before 3D generation (Real-ESRGAN)."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

#: Above this it's not worth enhancing — the 3D engine downsizes the image anyway.
_MAX_SIDE = 1024


def enhance(image, scale: int = 2):
    """Upscales and cleans the image. Returns the original if the upscaler is missing.

    Failing here must not block generation: an enhanced image is a bonus,
    not a requirement.
    """
    width, height = image.size
    if max(width, height) >= _MAX_SIDE:
        return image

    try:
        return _real_esrgan(image, scale)
    except Exception as exc:
        log.info("Real-ESRGAN unavailable (%s) — continuing with the original image.", exc)
        return _resample(image, scale)


def _real_esrgan(image, scale: int):  # pragma: no cover - depends on download
    import numpy as np
    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    model = RRDBNet(
        num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4
    )
    upsampler = RealESRGANer(
        scale=4,
        model_path=(
            "https://github.com/xinntao/Real-ESRGAN/releases/download/"
            "v0.1.0/RealESRGAN_x4plus.pth"
        ),
        model=model,
        half=torch.cuda.is_available(),
    )
    output, _ = upsampler.enhance(np.array(image.convert("RGB")), outscale=scale)

    from PIL import Image

    return Image.fromarray(output)


def _resample(image, scale: int):
    """Honest fallback: Lanczos resampling, no AI at all."""
    from PIL import Image

    width, height = image.size
    new_size = (min(width * scale, _MAX_SIDE), min(height * scale, _MAX_SIDE))
    return image.resize(new_size, Image.LANCZOS)
