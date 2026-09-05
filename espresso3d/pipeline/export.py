"""Exportação para todos os formatos, por dois caminhos.

* **trimesh** (puro Python): glb, gltf, obj, ply, stl, 3mf — sempre disponível.
* **Blender headless**: fbx, usdz, usdc, usda, dae, blend, vrm — precisa do
  Blender instalado, que é grátis mas é uma instalação à parte.

O caminho é escolhido pelo catálogo em :data:`espresso3d.config.FORMATOS`,
não por ``if`` espalhado pelo código.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import trimesh

from ..config import FORMATOS
from ..hardware import blender as achar_blender

log = logging.getLogger(__name__)

#: Formatos que geram arquivos soltos (textura, .mtl) e por isso vão zipados.
_ZIPAR = {"obj", "gltf"}


class BlenderNaoEncontrado(RuntimeError):
    def __init__(self, formatos: list[str]):
        exts = ", ".join(f".{f}" for f in formatos)
        super().__init__(
            f"Para exportar {exts} é preciso ter o Blender instalado.\n"
            "Baixe em https://www.blender.org/download/ (grátis) ou aponte "
            "a variável BLENDER_BIN para o executável.\n"
            "Os formatos .glb, .gltf, .obj, .ply, .stl e .3mf não precisam dele."
        )


def exportar(
    malha: trimesh.Trimesh,
    destino: Path,
    formatos: list[str],
    nome: str = "model",
) -> list[Path]:
    """Escreve ``malha`` em cada formato pedido dentro de ``destino``."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)

    desconhecidos = [f for f in formatos if f not in FORMATOS]
    if desconhecidos:
        raise ValueError(f"Formato desconhecido: {', '.join(desconhecidos)}")

    via_trimesh = [f for f in formatos if FORMATOS[f].backend == "trimesh"]
    via_blender = [f for f in formatos if FORMATOS[f].backend == "blender"]

    gerados: list[Path] = []
    for fmt in via_trimesh:
        gerados.append(_exportar_trimesh(malha, destino, fmt, nome))

    if via_blender:
        gerados.extend(_exportar_blender(malha, destino, via_blender, nome))

    return gerados


def _exportar_trimesh(
    malha: trimesh.Trimesh, destino: Path, fmt: str, nome: str
) -> Path:
    if fmt in _ZIPAR:
        return _exportar_zipado(malha, destino, fmt, nome)
    caminho = destino / f"{nome}.{fmt}"
    malha.export(caminho)
    return caminho


def _exportar_zipado(
    malha: trimesh.Trimesh, destino: Path, fmt: str, nome: str
) -> Path:
    """.obj e .gltf espalham arquivos — entrega tudo num zip só."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        malha.export(tmp_path / f"{nome}.{fmt}")
        zip_path = destino / f"{nome}_{fmt}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for arquivo in sorted(tmp_path.rglob("*")):
                if arquivo.is_file():
                    z.write(arquivo, arquivo.relative_to(tmp_path))
    return zip_path


def _exportar_blender(
    malha: trimesh.Trimesh, destino: Path, formatos: list[str], nome: str
) -> list[Path]:
    exe = achar_blender()
    if not exe:
        raise BlenderNaoEncontrado(formatos)

    with tempfile.TemporaryDirectory() as tmp:
        ponte = Path(tmp) / "ponte.glb"
        malha.export(ponte)

        saidas = {fmt: destino / f"{nome}.{fmt}" for fmt in formatos}
        script = Path(tmp) / "converter.py"
        script.write_text(
            _SCRIPT_BLENDER.format(
                entrada=repr(str(ponte)),
                saidas=repr({k: str(v) for k, v in saidas.items()}),
            ),
            encoding="utf-8",
        )

        resultado = subprocess.run(
            [exe, "--background", "--factory-startup", "--python", str(script)],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if resultado.returncode != 0:
            log.error("Blender falhou: %s", resultado.stderr[-2000:])
            raise RuntimeError(
                "O Blender não conseguiu converter os formatos "
                f"{', '.join(formatos)}. Detalhe: {resultado.stderr.strip()[-400:]}"
            )

    return [caminho for caminho in saidas.values() if caminho.exists()]


#: Roda dentro do Blender, não no interpretador do app.
_SCRIPT_BLENDER = '''
import bpy, sys

entrada = {entrada}
saidas = {saidas}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=entrada)

for fmt, caminho in saidas.items():
    try:
        if fmt == "fbx":
            bpy.ops.export_scene.fbx(filepath=caminho, path_mode="COPY", embed_textures=True)
        elif fmt == "dae":
            bpy.ops.wm.collada_export(filepath=caminho)
        elif fmt == "blend":
            bpy.ops.wm.save_as_mainfile(filepath=caminho)
        elif fmt in {{"usdz", "usdc", "usda"}}:
            bpy.ops.wm.usd_export(filepath=caminho, export_textures=True)
        elif fmt == "vrm":
            # Depende do addon VRM instalado no Blender; sem ele, avisa e segue.
            bpy.ops.export_scene.vrm(filepath=caminho)
    except Exception as exc:
        print("ESPRESSO3D_FALHA %s: %s" % (fmt, exc), file=sys.stderr)
'''


def blender_disponivel() -> bool:
    return achar_blender() is not None


def limpar_saida(pasta: Path) -> None:
    """Apaga uma pasta de saída pela metade (usado quando a geração falha)."""
    shutil.rmtree(pasta, ignore_errors=True)
