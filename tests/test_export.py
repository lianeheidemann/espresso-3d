import zipfile

import pytest
import trimesh

from espresso3d.pipeline import export


@pytest.fixture
def mesh():
    return trimesh.creation.icosphere(subdivisions=2)


def test_exports_glb(mesh, tmp_path):
    generated = export.export(mesh, tmp_path, ["glb"], name="test")
    assert len(generated) == 1
    assert generated[0].name == "test.glb"
    assert generated[0].stat().st_size > 0


def test_exports_several_light_formats(mesh, tmp_path):
    generated = export.export(mesh, tmp_path, ["glb", "stl", "ply"], name="m")
    names = sorted(p.name for p in generated)
    assert names == ["m.glb", "m.ply", "m.stl"]
    assert all(p.stat().st_size > 0 for p in generated)


def test_obj_comes_out_zipped_with_the_mtl(mesh, tmp_path):
    generated = export.export(mesh, tmp_path, ["obj"], name="m")
    assert generated[0].suffix == ".zip"

    with zipfile.ZipFile(generated[0]) as z:
        assert any(n.endswith(".obj") for n in z.namelist())


def test_glb_is_reimportable(mesh, tmp_path):
    path = export.export(mesh, tmp_path, ["glb"], name="m")[0]
    scene = trimesh.load(path)
    faces = sum(len(g.faces) for g in scene.geometry.values())
    assert faces == len(mesh.faces)


def test_unknown_format(mesh, tmp_path):
    with pytest.raises(ValueError, match="Unknown"):
        export.export(mesh, tmp_path, ["xyz"], name="m")


def test_creates_the_destination_folder(mesh, tmp_path):
    destination = tmp_path / "new" / "folder"
    export.export(mesh, destination, ["glb"], name="m")
    assert destination.exists()


def test_blender_error_explains_what_to_do(mesh, tmp_path, monkeypatch):
    monkeypatch.setattr(export, "find_blender", lambda: None)

    with pytest.raises(export.BlenderNotFound) as exc:
        export.export(mesh, tmp_path, ["fbx"], name="m")

    message = str(exc.value)
    assert "blender.org" in message
    assert ".fbx" in message
    assert ".glb" in message  # says which formats work without it


def test_light_formats_work_even_without_blender(mesh, tmp_path, monkeypatch):
    monkeypatch.setattr(export, "find_blender", lambda: None)
    generated = export.export(mesh, tmp_path, ["glb"], name="m")
    assert generated[0].exists()
