import zipfile

import pytest
import trimesh

from espresso3d.pipeline import export


@pytest.fixture
def malha():
    return trimesh.creation.icosphere(subdivisions=2)


def test_exporta_glb(malha, tmp_path):
    gerados = export.exportar(malha, tmp_path, ["glb"], nome="teste")
    assert len(gerados) == 1
    assert gerados[0].name == "teste.glb"
    assert gerados[0].stat().st_size > 0


def test_exporta_varios_formatos_leves(malha, tmp_path):
    gerados = export.exportar(malha, tmp_path, ["glb", "stl", "ply"], nome="m")
    nomes = sorted(p.name for p in gerados)
    assert nomes == ["m.glb", "m.ply", "m.stl"]
    assert all(p.stat().st_size > 0 for p in gerados)


def test_obj_sai_zipado_com_o_mtl(malha, tmp_path):
    gerados = export.exportar(malha, tmp_path, ["obj"], nome="m")
    assert gerados[0].suffix == ".zip"

    with zipfile.ZipFile(gerados[0]) as z:
        assert any(n.endswith(".obj") for n in z.namelist())


def test_glb_reimportavel(malha, tmp_path):
    caminho = export.exportar(malha, tmp_path, ["glb"], nome="m")[0]
    cena = trimesh.load(caminho)
    faces = sum(len(g.faces) for g in cena.geometry.values())
    assert faces == len(malha.faces)


def test_formato_desconhecido(malha, tmp_path):
    with pytest.raises(ValueError, match="desconhecido"):
        export.exportar(malha, tmp_path, ["xyz"], nome="m")


def test_cria_a_pasta_de_destino(malha, tmp_path):
    destino = tmp_path / "nova" / "pasta"
    export.exportar(malha, destino, ["glb"], nome="m")
    assert destino.exists()


def test_erro_de_blender_explica_o_que_fazer(malha, tmp_path, monkeypatch):
    monkeypatch.setattr(export, "achar_blender", lambda: None)

    with pytest.raises(export.BlenderNaoEncontrado) as exc:
        export.exportar(malha, tmp_path, ["fbx"], nome="m")

    mensagem = str(exc.value)
    assert "blender.org" in mensagem
    assert ".fbx" in mensagem
    assert ".glb" in mensagem  # diz quais formatos funcionam sem ele


def test_formatos_leves_saem_mesmo_sem_blender(malha, tmp_path, monkeypatch):
    monkeypatch.setattr(export, "achar_blender", lambda: None)
    gerados = export.exportar(malha, tmp_path, ["glb"], nome="m")
    assert gerados[0].exists()
