"""Orchestrator: chains the stages according to the chosen configuration.

    image → enhancement → segmentation → 3D generation → mesh → rig → export

Each stage is optional and fails in isolation: if rigging isn't
available, the model is still generated and exported, with the warning
recorded in the result.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ..config import PipelineConfig, Pose
from ..engines import get as get_engine
from . import enhance, export, mesh_post, rigging, segment

log = logging.getLogger(__name__)

OUTPUT_ROOT = Path("outputs")


@dataclass
class Result:
    """What a generation produced — including whatever went wrong along the way."""

    folder: Path
    files: list[Path] = field(default_factory=list)
    parts: int = 1
    stats: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    duration_s: float = 0.0

    @property
    def preview(self) -> Path | None:
        """The .glb is used as a preview in the UI's viewer."""
        for file in self.files:
            if file.suffix == ".glb":
                return file
        return None


def generate(
    image,
    cfg: PipelineConfig,
    name: str = "model",
    root: Path = OUTPUT_ROOT,
    progress=None,
    backend_llm=None,
) -> Result:
    """Runs the whole pipeline for one image."""
    cfg.validate()
    start = time.monotonic()
    warnings: list[str] = []

    def notify(step: str, fraction: float) -> None:
        if progress is not None:
            progress(fraction, desc=step)

    folder = _create_folder(root, name)
    image.save(folder / "source.png")

    if cfg.enhance_image:
        notify("Enhancing the image", 0.1)
        image = enhance.enhance(image)

    notify("Splitting the parts" if cfg.split_parts else "Preparing", 0.2)
    crops = segment.separate_objects(image) if cfg.split_parts else [image]

    engine = get_engine(cfg.engine)
    meshes = []
    for i, crop in enumerate(crops, start=1):
        notify(f"Generating 3D ({i}/{len(crops)})", 0.2 + 0.5 * i / len(crops))
        mesh = engine.generate(crop, cfg)
        mesh = mesh_post.adjust_poly_count(mesh, cfg.poly_count_target, cfg.topology)
        meshes.append(mesh)

    if cfg.pose is not Pose.NONE:
        notify("Applying skeleton and pose", 0.8)
        try:
            meshes = [rigging.apply_rig(m, cfg, backend_llm)[0] for m in meshes]
        except rigging.RigUnavailable as exc:
            warnings.append(f"No rig: {exc}")

    notify("Exporting", 0.9)
    files: list[Path] = []
    for i, mesh in enumerate(meshes, start=1):
        suffix = name if len(meshes) == 1 else f"{name}_part{i}"
        try:
            files += export.export(mesh, folder, cfg.formats, suffix)
        except export.BlenderNotFound as exc:
            warnings.append(str(exc))
            light_only = [
                f for f in cfg.formats if f not in cfg.needs_blender
            ] or ["glb"]
            files += export.export(mesh, folder, light_only, suffix)

    warnings += cfg.warnings()
    result = Result(
        folder=folder,
        files=files,
        parts=len(meshes),
        stats=mesh_post.stats(meshes[0]) if meshes else {},
        warnings=warnings,
        duration_s=round(time.monotonic() - start, 1),
    )

    from ..library.store import register

    register(result, cfg, name)
    return result


def generate_batch(
    images: list,
    cfg: PipelineConfig,
    names: list[str] | None = None,
    root: Path = OUTPUT_ROOT,
    progress=None,
    backend_llm=None,
) -> list[Result]:
    """Runs the pipeline for several images, one at a time.

    Sequential on purpose: with 4-8GB of VRAM, two generations in
    parallel blow up the GPU memory and both fail.

    All of them use the SAME configuration from the "Image → 3D" tab —
    the batch tab has no panel of its own.
    """
    names = names or [f"model_{i + 1}" for i in range(len(images))]
    results: list[Result] = []

    for i, (image, name) in enumerate(zip(images, names), start=1):
        if progress is not None:
            progress((i - 1) / len(images), desc=f"Image {i} of {len(images)}")
        try:
            results.append(
                generate(image, cfg, name=name, root=root, backend_llm=backend_llm)
            )
        except Exception as exc:
            log.exception("Failed on image %s of the batch", i)
            results.append(
                Result(folder=root / name, warnings=[f"Failed: {exc}"])
            )

    return results


def _create_folder(root: Path, name: str) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder = Path(root) / f"{stamp}_{_clean_name(name)}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _clean_name(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.strip())
    return (safe.strip("_") or "model")[:60]
