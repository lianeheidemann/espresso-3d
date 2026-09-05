import pytest

from espresso3d.config import (
    Licenca,
    PipelineConfig,
    Pose,
    ResolucaoTextura,
    Topologia,
    formatos_por_grupo,
)


def test_padrao_e_valido():
    PipelineConfig().validar()


def test_exige_pelo_menos_um_formato():
    with pytest.raises(ValueError, match="pelo menos um formato"):
        PipelineConfig(formatos=[]).validar()


def test_rejeita_formato_desconhecido():
    with pytest.raises(ValueError, match="desconhecido"):
        PipelineConfig(formatos=["glb", "xyz"]).validar()


def test_poly_count_fora_da_faixa():
    with pytest.raises(ValueError, match="polígonos"):
        PipelineConfig(poly_count_alvo=99).validar()
    with pytest.raises(ValueError, match="polígonos"):
        PipelineConfig(poly_count_alvo=999_999).validar()


def test_pose_custom_exige_descricao_ou_foto():
    with pytest.raises(ValueError, match="descrição em texto"):
        PipelineConfig(pose=Pose.CUSTOM).validar()

    PipelineConfig(pose=Pose.CUSTOM, pose_prompt="braços abertos").validar()
    PipelineConfig(pose=Pose.CUSTOM, pose_ref_imagem="/tmp/foto.png").validar()


def test_aviso_de_stl_sem_textura():
    avisos = PipelineConfig(formatos=["stl"], gerar_textura=True).avisos()
    assert any("stl" in a and "textura" in a for a in avisos)


def test_sem_aviso_de_textura_quando_textura_desligada():
    avisos = PipelineConfig(formatos=["stl"], gerar_textura=False).avisos()
    assert not any("não guarda textura" in a for a in avisos)


def test_aviso_de_rig_perdido_so_com_pose():
    com_pose = PipelineConfig(
        formatos=["obj"], pose=Pose.T_POSE
    ).avisos()
    assert any("esqueleto" in a for a in com_pose)

    sem_pose = PipelineConfig(formatos=["obj"], pose=Pose.NENHUM).avisos()
    assert not any("esqueleto" in a for a in sem_pose)


def test_glb_nao_gera_aviso_de_perda():
    avisos = PipelineConfig(formatos=["glb"], pose=Pose.T_POSE).avisos()
    assert avisos == []


def test_formatos_que_precisam_de_blender():
    cfg = PipelineConfig(formatos=["glb", "fbx", "usdz", "stl"])
    assert sorted(cfg.precisa_blender) == ["fbx", "usdz"]


def test_roundtrip_dict():
    original = PipelineConfig(
        engine="tripo_sr",
        topologia=Topologia.SMART,
        pose=Pose.CUSTOM,
        pose_prompt="sentado",
        licenca=Licenca.COMERCIAL,
        resolucao_textura=ResolucaoTextura.ULTRA_2K,
        formatos=["glb", "fbx"],
    )
    voltou = PipelineConfig.de_dict(original.como_dict())
    assert voltou == original
    assert voltou.resolucao_textura.pixels == 2048


def test_de_dict_ignora_chave_desconhecida():
    cfg = PipelineConfig.de_dict({"engine": "tripo_sr", "campo_inventado": 42})
    assert cfg.engine == "tripo_sr"


def test_formatos_agrupados_cobrem_o_catalogo():
    grupos = formatos_por_grupo()
    total = sum(len(v) for v in grupos.values())
    assert total >= 13
    assert "Web e AR no Android" in grupos
