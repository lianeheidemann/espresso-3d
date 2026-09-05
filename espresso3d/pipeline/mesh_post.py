"""Pós-processamento da malha: limpeza e redução até a contagem alvo."""

from __future__ import annotations

import logging

import trimesh

from ..config import Topologia

log = logging.getLogger(__name__)


def limpar(malha: trimesh.Trimesh) -> trimesh.Trimesh:
    """Remove lixo geométrico que os geradores costumam deixar."""
    malha.update_faces(malha.nondegenerate_faces())
    malha.update_faces(malha.unique_faces())
    malha.remove_unreferenced_vertices()
    return malha


def ajustar_poly_count(
    malha: trimesh.Trimesh,
    alvo: int,
    topologia: Topologia = Topologia.ALTO_DETALHE,
) -> trimesh.Trimesh:
    """Reduz a malha até ~``alvo`` faces.

    "Smart topology" costura vértices duplicados antes de reduzir, o que
    gera uma malha mais limpa para rig e animação; "alto detalhe" reduz
    direto, preservando melhor a silhueta original.

    Malha com menos faces que o alvo volta intacta — subdividir para
    inflar a contagem só criaria geometria sem informação nenhuma.
    """
    if alvo <= 0:
        raise ValueError("A contagem de polígonos alvo precisa ser positiva.")

    if topologia is Topologia.SMART:
        malha = limpar(malha.copy())
        malha.merge_vertices()
    else:
        malha = malha.copy()

    if len(malha.faces) <= alvo:
        return malha

    try:
        return malha.simplify_quadric_decimation(face_count=alvo)
    except Exception as exc:  # pragma: no cover - depende de dependência opcional
        log.warning(
            "Não foi possível reduzir a malha (%s). "
            "Instale 'fast-simplification' para respeitar a contagem de polígonos.",
            exc,
        )
        return malha


def estatisticas(malha: trimesh.Trimesh) -> dict:
    """Números que a interface mostra embaixo do modelo."""
    return {
        "faces": len(malha.faces),
        "vertices": len(malha.vertices),
        "tem_uv": bool(
            getattr(malha.visual, "uv", None) is not None
            and len(getattr(malha.visual, "uv", []))
        ),
        "watertight": bool(malha.is_watertight),
    }


def separar_partes(malha: trimesh.Trimesh) -> list[trimesh.Trimesh]:
    """Separa corpos desconectados em malhas independentes.

    Usado quando o usuário liga "Dividir em partes": a xícara e o pires
    saem como dois objetos, não como um sólido único.
    """
    try:
        partes = malha.split(only_watertight=False)
    except ImportError:
        # trimesh precisa de scipy (ou networkx) para achar componentes conexos.
        log.warning(
            "Separação de partes indisponível: falta scipy. "
            "Instale com 'pip install scipy'. Seguindo com o objeto inteiro."
        )
        return [malha]
    return list(partes) if len(partes) else [malha]
