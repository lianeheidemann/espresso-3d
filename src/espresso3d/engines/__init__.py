"""Registro dos motores de geração 3D.

Adicionar um motor novo é criar o módulo e acrescentar uma linha em
:data:`MOTORES` — a interface se atualiza sozinha a partir daqui.
"""

from __future__ import annotations

from ..config import Licenca
from .base import DependenciaFaltando, InfoMotor, Motor
from .instant_mesh import InstantMesh
from .stable_fast_3d import StableFast3D
from .tripo_sr import TripoSR

MOTORES: dict[str, Motor] = {
    m.info.id: m
    for m in (TripoSR(), StableFast3D(), InstantMesh())
}

__all__ = [
    "MOTORES",
    "Motor",
    "InfoMotor",
    "DependenciaFaltando",
    "obter",
    "listar",
    "sugerir",
]


def obter(id_motor: str) -> Motor:
    if id_motor not in MOTORES:
        conhecidos = ", ".join(MOTORES)
        raise KeyError(f"Motor '{id_motor}' não existe. Disponíveis: {conhecidos}")
    return MOTORES[id_motor]


def listar(licenca: Licenca | None = None, vram_gb: float | None = None) -> list[Motor]:
    """Motores compatíveis com a licença pedida e com a GPU da máquina."""
    motores = list(MOTORES.values())
    if licenca is not None:
        motores = [m for m in motores if m.compativel_com(licenca)]
    if vram_gb is not None:
        motores = [m for m in motores if m.info.vram_min_gb <= vram_gb + 0.5]
    return motores


def sugerir(vram_gb: float | None = None, licenca: Licenca | None = None) -> Motor:
    """O melhor motor que cabe na GPU disponível.

    Sem GPU detectada, devolve o mais leve: é o único que roda na CPU em
    tempo tolerável.
    """
    candidatos = listar(licenca=licenca, vram_gb=vram_gb)
    if not candidatos:
        return obter("tripo_sr")
    return max(candidatos, key=lambda m: m.info.vram_min_gb)
