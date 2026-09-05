"""Mesh post-processing: cleanup and decimation down to the target count."""

from __future__ import annotations

import logging

import trimesh

from ..config import Topology

log = logging.getLogger(__name__)


def clean(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Removes geometric junk that generators tend to leave behind."""
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def adjust_poly_count(
    mesh: trimesh.Trimesh,
    target: int,
    topology: Topology = Topology.HIGH_DETAIL,
) -> trimesh.Trimesh:
    """Reduces the mesh down to ~``target`` faces.

    "Smart topology" stitches duplicate vertices before reducing, which
    produces a cleaner mesh for rigging and animation; "high detail"
    reduces directly, preserving the original silhouette better.

    A mesh with fewer faces than the target comes back untouched —
    subdividing to inflate the count would only create geometry with no
    information in it.
    """
    if target <= 0:
        raise ValueError("The target polygon count must be positive.")

    if topology is Topology.SMART:
        mesh = clean(mesh.copy())
        mesh.merge_vertices()
    else:
        mesh = mesh.copy()

    if len(mesh.faces) <= target:
        return mesh

    try:
        return mesh.simplify_quadric_decimation(face_count=target)
    except Exception as exc:  # pragma: no cover - depends on an optional dependency
        log.warning(
            "Couldn't reduce the mesh (%s). "
            "Install 'fast-simplification' to honor the polygon count.",
            exc,
        )
        return mesh


def stats(mesh: trimesh.Trimesh) -> dict:
    """Numbers the UI shows below the model."""
    return {
        "faces": len(mesh.faces),
        "vertices": len(mesh.vertices),
        "has_uv": bool(
            getattr(mesh.visual, "uv", None) is not None
            and len(getattr(mesh.visual, "uv", []))
        ),
        "watertight": bool(mesh.is_watertight),
    }


def split_parts(mesh: trimesh.Trimesh) -> list[trimesh.Trimesh]:
    """Splits disconnected bodies into independent meshes.

    Used when the user turns on "Split into parts": the cup and the
    saucer come out as two objects, not as a single fused solid.
    """
    try:
        parts = mesh.split(only_watertight=False)
    except ImportError:
        # trimesh needs scipy (or networkx) to find connected components.
        log.warning(
            "Part splitting unavailable: scipy is missing. "
            "Install with 'pip install scipy'. Continuing with the whole object."
        )
        return [mesh]
    return list(parts) if len(parts) else [mesh]
