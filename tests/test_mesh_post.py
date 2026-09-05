import trimesh

from espresso3d.config import Topologia
from espresso3d.pipeline import mesh_post


def esfera(subdiv=4):
    return trimesh.creation.icosphere(subdivisions=subdiv)


def test_reduz_ate_o_alvo():
    malha = esfera()
    assert len(malha.faces) > 4000

    reduzida = mesh_post.ajustar_poly_count(malha, 1000)
    assert len(reduzida.faces) <= 1100  # tolera arredondamento do algoritmo


def test_malha_menor_que_o_alvo_fica_intacta():
    malha = esfera(subdiv=1)
    faces = len(malha.faces)

    resultado = mesh_post.ajustar_poly_count(malha, 50_000)
    assert len(resultado.faces) == faces


def test_nao_modifica_a_malha_original():
    malha = esfera()
    antes = len(malha.faces)

    mesh_post.ajustar_poly_count(malha, 500)
    assert len(malha.faces) == antes


def test_smart_topology_tambem_reduz():
    malha = esfera()
    reduzida = mesh_post.ajustar_poly_count(malha, 800, Topologia.SMART)
    assert len(reduzida.faces) <= 900


def test_alvo_invalido():
    import pytest

    with pytest.raises(ValueError):
        mesh_post.ajustar_poly_count(esfera(), 0)


def test_estatisticas():
    est = mesh_post.estatisticas(esfera(subdiv=2))
    assert est["faces"] > 0
    assert est["vertices"] > 0
    assert est["watertight"] is True


def test_separar_partes_encontra_dois_corpos():
    a = trimesh.creation.box(extents=[1, 1, 1])
    b = trimesh.creation.box(extents=[1, 1, 1])
    b.apply_translation([5, 0, 0])
    juntos = trimesh.util.concatenate([a, b])

    partes = mesh_post.separar_partes(juntos)
    assert len(partes) == 2


def test_separar_partes_de_corpo_unico():
    partes = mesh_post.separar_partes(esfera(subdiv=1))
    assert len(partes) == 1
