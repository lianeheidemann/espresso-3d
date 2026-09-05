import trimesh

from espresso3d.config import Topology
from espresso3d.pipeline import mesh_post


def sphere(subdiv=4):
    return trimesh.creation.icosphere(subdivisions=subdiv)


def test_reduces_to_the_target():
    mesh = sphere()
    assert len(mesh.faces) > 4000

    reduced = mesh_post.adjust_poly_count(mesh, 1000)
    assert len(reduced.faces) <= 1100  # tolerates algorithm rounding


def test_mesh_smaller_than_target_stays_intact():
    mesh = sphere(subdiv=1)
    faces = len(mesh.faces)

    result = mesh_post.adjust_poly_count(mesh, 50_000)
    assert len(result.faces) == faces


def test_does_not_modify_the_original_mesh():
    mesh = sphere()
    before = len(mesh.faces)

    mesh_post.adjust_poly_count(mesh, 500)
    assert len(mesh.faces) == before


def test_smart_topology_also_reduces():
    mesh = sphere()
    reduced = mesh_post.adjust_poly_count(mesh, 800, Topology.SMART)
    assert len(reduced.faces) <= 900


def test_invalid_target():
    import pytest

    with pytest.raises(ValueError):
        mesh_post.adjust_poly_count(sphere(), 0)


def test_stats():
    st = mesh_post.stats(sphere(subdiv=2))
    assert st["faces"] > 0
    assert st["vertices"] > 0
    assert st["watertight"] is True


def test_split_parts_finds_two_bodies():
    a = trimesh.creation.box(extents=[1, 1, 1])
    b = trimesh.creation.box(extents=[1, 1, 1])
    b.apply_translation([5, 0, 0])
    together = trimesh.util.concatenate([a, b])

    parts = mesh_post.split_parts(together)
    assert len(parts) == 2


def test_split_parts_of_a_single_body():
    parts = mesh_post.split_parts(sphere(subdiv=1))
    assert len(parts) == 1
