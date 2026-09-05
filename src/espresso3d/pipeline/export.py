"""Export to every format, via two paths.

* **trimesh** (pure Python): glb, gltf, obj, ply, stl, 3mf — always available.
* **Headless Blender**: fbx, usdz, usdc, usda, dae, blend, vrm — needs
  Blender installed, which is free but a separate install.

The path is chosen by the catalog in :data:`espresso3d.config.FORMATS`,
not by ``if`` statements scattered through the code.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import trimesh

from ..config import FORMATS
from ..hardware import blender as find_blender

log = logging.getLogger(__name__)

#: Formats that produce loose files (texture, .mtl) and are therefore zipped.
_ZIP = {"obj", "gltf"}


class BlenderNotFound(RuntimeError):
    def __init__(self, formats: list[str]):
        exts = ", ".join(f".{f}" for f in formats)
        super().__init__(
            f"To export {exts} you need Blender installed.\n"
            "Download it at https://www.blender.org/download/ (free) or point "
            "the BLENDER_BIN variable to the executable.\n"
            "The .glb, .gltf, .obj, .ply, .stl and .3mf formats don't need it."
        )


def export(
    mesh: trimesh.Trimesh,
    destination: Path,
    formats: list[str],
    name: str = "model",
) -> list[Path]:
    """Writes ``mesh`` in each requested format inside ``destination``."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    unknown = [f for f in formats if f not in FORMATS]
    if unknown:
        raise ValueError(f"Unknown format: {', '.join(unknown)}")

    via_trimesh = [f for f in formats if FORMATS[f].backend == "trimesh"]
    via_blender = [f for f in formats if FORMATS[f].backend == "blender"]

    generated: list[Path] = []
    for fmt in via_trimesh:
        generated.append(_export_trimesh(mesh, destination, fmt, name))

    if via_blender:
        generated.extend(_export_blender(mesh, destination, via_blender, name))

    return generated


def _export_trimesh(
    mesh: trimesh.Trimesh, destination: Path, fmt: str, name: str
) -> Path:
    if fmt in _ZIP:
        return _export_zipped(mesh, destination, fmt, name)
    path = destination / f"{name}.{fmt}"
    mesh.export(path)
    return path


def _export_zipped(
    mesh: trimesh.Trimesh, destination: Path, fmt: str, name: str
) -> Path:
    """.obj and .gltf spread files around — deliver everything in one zip."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        mesh.export(tmp_path / f"{name}.{fmt}")
        zip_path = destination / f"{name}_{fmt}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for file in sorted(tmp_path.rglob("*")):
                if file.is_file():
                    z.write(file, file.relative_to(tmp_path))
    return zip_path


def _export_blender(
    mesh: trimesh.Trimesh, destination: Path, formats: list[str], name: str
) -> list[Path]:
    exe = find_blender()
    if not exe:
        raise BlenderNotFound(formats)

    with tempfile.TemporaryDirectory() as tmp:
        bridge = Path(tmp) / "bridge.glb"
        mesh.export(bridge)

        outputs = {fmt: destination / f"{name}.{fmt}" for fmt in formats}
        script = Path(tmp) / "converter.py"
        script.write_text(
            _BLENDER_SCRIPT.format(
                input_path=repr(str(bridge)),
                outputs=repr({k: str(v) for k, v in outputs.items()}),
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [exe, "--background", "--factory-startup", "--python", str(script)],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            log.error("Blender failed: %s", result.stderr[-2000:])
            raise RuntimeError(
                "Blender couldn't convert the formats "
                f"{', '.join(formats)}. Detail: {result.stderr.strip()[-400:]}"
            )

    return [path for path in outputs.values() if path.exists()]


#: Runs inside Blender, not the app's interpreter.
_BLENDER_SCRIPT = '''
import bpy, sys

input_path = {input_path}
outputs = {outputs}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=input_path)

for fmt, path in outputs.items():
    try:
        if fmt == "fbx":
            bpy.ops.export_scene.fbx(filepath=path, path_mode="COPY", embed_textures=True)
        elif fmt == "dae":
            bpy.ops.wm.collada_export(filepath=path)
        elif fmt == "blend":
            bpy.ops.wm.save_as_mainfile(filepath=path)
        elif fmt in {{"usdz", "usdc", "usda"}}:
            bpy.ops.wm.usd_export(filepath=path, export_textures=True)
        elif fmt == "vrm":
            # Depends on the VRM add-on installed in Blender; without it, warns and continues.
            bpy.ops.export_scene.vrm(filepath=path)
    except Exception as exc:
        print("ESPRESSO3D_FAILURE %s: %s" % (fmt, exc), file=sys.stderr)
'''


def blender_available() -> bool:
    return find_blender() is not None


def clear_output(folder: Path) -> None:
    """Deletes a half-finished output folder (used when generation fails)."""
    shutil.rmtree(folder, ignore_errors=True)
