from espresso3d.agent import parser
from espresso3d.config import Licenca, PipelineConfig, Pose, ResolucaoTextura


class CerebroFalso:
    """Devolve uma resposta fixa, para testar sem LLM nenhum."""

    def __init__(self, resposta):
        self.resposta = resposta

    def completar(self, prompt):
        return self.resposta


def test_palavras_chave_detecta_divisao():
    cfg = parser.por_palavras_chave("gera a xícara separada do pires")
    assert cfg.dividir_partes is True


def test_palavras_chave_alta_qualidade():
    cfg = parser.por_palavras_chave("quero em alta qualidade")
    assert cfg.engine == "instant_mesh"
    assert cfg.resolucao_textura is ResolucaoTextura.ULTRA_2K


def test_palavras_chave_rapido():
    cfg = parser.por_palavras_chave("faz rápido, é só um rascunho")
    assert cfg.engine == "tripo_sr"


def test_palavras_chave_formato():
    cfg = parser.por_palavras_chave("exporta em .fbx e .usdz")
    assert sorted(cfg.formatos) == ["fbx", "usdz"]


def test_palavras_chave_sem_textura():
    cfg = parser.por_palavras_chave("só a malha, sem textura")
    assert cfg.gerar_textura is False


def test_palavras_chave_pose():
    assert parser.por_palavras_chave("em t-pose").pose is Pose.T_POSE
    assert parser.por_palavras_chave("em a-pose").pose is Pose.A_POSE


def test_palavras_chave_licenca_comercial():
    assert parser.por_palavras_chave("uso comercial").licenca is Licenca.COMERCIAL


def test_palavras_chave_contagem_de_poligonos():
    cfg = parser.por_palavras_chave("com 8.000 polígonos")
    assert cfg.poly_count_alvo == 8000


def test_palavras_chave_preserva_o_resto():
    base = PipelineConfig(melhorar_imagem=False, formatos=["glb"])
    cfg = parser.por_palavras_chave("separado", base)
    assert cfg.melhorar_imagem is False
    assert cfg.formatos == ["glb"]


def test_aplicar_ignora_motor_inexistente():
    cfg = parser.aplicar({"engine": "motor_que_nao_existe"}, PipelineConfig())
    assert cfg.engine == "stable_fast_3d"


def test_aplicar_limita_poly_count():
    assert parser.aplicar({"poly_count_alvo": 99_999}, PipelineConfig()).poly_count_alvo == 20_000
    assert parser.aplicar({"poly_count_alvo": 1}, PipelineConfig()).poly_count_alvo == 500


def test_aplicar_ignora_enum_invalido():
    cfg = parser.aplicar({"pose": "voando"}, PipelineConfig())
    assert cfg.pose is Pose.NENHUM


def test_pose_prompt_liga_pose_customizada():
    cfg = parser.aplicar({"pose_prompt": "sentado no chão"}, PipelineConfig())
    assert cfg.pose is Pose.CUSTOM


def test_llm_com_json_valido():
    cerebro = CerebroFalso('{"engine": "tripo_sr", "dividir_partes": true}')
    cfg = parser.do_llm("qualquer coisa", cerebro)
    assert cfg.engine == "tripo_sr"
    assert cfg.dividir_partes is True


def test_llm_com_json_embrulhado_em_conversa():
    cerebro = CerebroFalso(
        'Claro! Aqui está:\n```json\n{"poly_count_alvo": 9000}\n```\nEspero ter ajudado.'
    )
    cfg = parser.do_llm("...", cerebro)
    assert cfg.poly_count_alvo == 9000


def test_llm_sem_json_cai_no_modo_basico():
    cerebro = CerebroFalso("desculpe, não entendi")
    cfg = parser.do_llm("quero separado do pires", cerebro)
    assert cfg.dividir_partes is True


def test_llm_que_explode_cai_no_modo_basico():
    class Quebrado:
        def completar(self, prompt):
            raise RuntimeError("ollama offline")

    cfg = parser.do_llm("em alta qualidade", Quebrado())
    assert cfg.engine == "instant_mesh"


def test_resumo_tem_as_chaves_do_card():
    resumo = parser.resumo(PipelineConfig())
    assert "Motor" in resumo
    assert "Formatos" in resumo
    assert resumo["Formatos"] == ".glb"
