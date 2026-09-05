import pytest

from espresso3d import engines
from espresso3d.config import Licenca


def test_registro_tem_os_tres_motores():
    assert set(engines.MOTORES) == {"tripo_sr", "stable_fast_3d", "instant_mesh"}


def test_obter_motor_inexistente_lista_os_validos():
    with pytest.raises(KeyError, match="tripo_sr"):
        engines.obter("motor_fantasma")


def test_filtro_por_vram():
    cabem_em_4gb = engines.listar(vram_gb=4)
    assert [m.info.id for m in cabem_em_4gb] == ["tripo_sr"]

    cabem_em_8gb = engines.listar(vram_gb=8)
    assert len(cabem_em_8gb) == 3


def test_filtro_por_licenca_comercial():
    """A licença da Stability restringe uso comercial — o filtro respeita isso."""
    comerciais = {m.info.id for m in engines.listar(licenca=Licenca.COMERCIAL)}
    assert "stable_fast_3d" not in comerciais
    assert "tripo_sr" in comerciais


def test_licenca_privada_libera_todos():
    privados = engines.listar(licenca=Licenca.PRIVADA)
    assert len(privados) == 3


def test_sugerir_pega_o_melhor_que_cabe():
    assert engines.sugerir(vram_gb=8).info.id == "instant_mesh"
    assert engines.sugerir(vram_gb=6).info.id == "stable_fast_3d"
    assert engines.sugerir(vram_gb=4).info.id == "tripo_sr"


def test_sugerir_sem_gpu_devolve_o_mais_leve():
    assert engines.sugerir(vram_gb=0).info.id == "tripo_sr"


def test_sugerir_respeita_licenca():
    escolhido = engines.sugerir(vram_gb=6, licenca=Licenca.COMERCIAL)
    assert escolhido.info.uso_comercial is True


def test_motor_recusa_gpu_pequena_com_mensagem_util():
    motor = engines.obter("instant_mesh")
    from espresso3d.engines import base

    original = base._vram
    base._vram = lambda: 4.0
    try:
        with pytest.raises(RuntimeError, match="8 GB de VRAM"):
            motor.gerar(None, None)
    finally:
        base._vram = original


def test_metadados_completos():
    for motor in engines.MOTORES.values():
        info = motor.info
        assert info.nome and info.descricao and info.repo
        assert info.vram_min_gb > 0
        assert info.licenca_pesos
