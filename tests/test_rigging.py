from espresso3d.pipeline import rigging

OSSOS = rigging.OSSOS_HUMANOIDES


def test_aceita_rotacao_valida():
    limpo = rigging.validar_rotacoes({"head": [0, 25, 0]}, OSSOS)
    assert limpo == {"head": [0.0, 25.0, 0.0]}


def test_descarta_osso_que_nao_existe_no_rig():
    limpo = rigging.validar_rotacoes(
        {"asa_esquerda": [0, 0, 0], "head": [1, 2, 3]}, OSSOS
    )
    assert list(limpo) == ["head"]


def test_limita_angulo_absurdo():
    limpo = rigging.validar_rotacoes({"right_upper_arm": [900, -900, 0]}, OSSOS)
    assert limpo["right_upper_arm"] == [180.0, -180.0, 0.0]


def test_descarta_formato_errado():
    bruto = {
        "head": [1, 2],           # faltando um eixo
        "neck": "muito girado",   # nem é lista
        "spine": [1, 2, "x"],     # valor não numérico
        "hips": [0, 10, 0],       # este é o único bom
    }
    assert list(rigging.validar_rotacoes(bruto, OSSOS)) == ["hips"]


def test_normaliza_o_nome_do_osso():
    limpo = rigging.validar_rotacoes({"Right Upper Arm": [0, 0, 10]}, OSSOS)
    assert "right_upper_arm" in limpo


def test_entrada_vazia():
    assert rigging.validar_rotacoes({}, OSSOS) == {}
    assert rigging.validar_rotacoes(None, OSSOS) == {}


def test_extrai_json_puro():
    assert rigging.extrair_json('{"head": [0, 0, 0]}') == {"head": [0, 0, 0]}


def test_extrai_json_de_bloco_de_codigo():
    texto = '```json\n{"neck": [1, 2, 3]}\n```'
    assert rigging.extrair_json(texto) == {"neck": [1, 2, 3]}


def test_extrai_json_com_conversa_em_volta():
    texto = 'Claro! Segue: {"hips": [0, 0, 5]} — espero que ajude!'
    assert rigging.extrair_json(texto) == {"hips": [0, 0, 5]}


def test_extrai_json_de_texto_sem_json():
    assert rigging.extrair_json("não consegui fazer isso") == {}
    assert rigging.extrair_json("") == {}


def test_pose_por_texto_ponta_a_ponta():
    class Cerebro:
        def completar(self, prompt):
            assert "right_upper_arm" in prompt  # recebeu a lista de ossos real
            return '{"right_upper_arm": [0, 0, -75], "asa": [1, 1, 1]}'

    pose = rigging.pose_por_texto("braço direito levantado", OSSOS, Cerebro())
    assert pose == {"right_upper_arm": [0.0, 0.0, -75.0]}


def test_pose_por_texto_vazio_nao_chama_o_llm():
    class NuncaChamado:
        def completar(self, prompt):
            raise AssertionError("não deveria chamar o LLM com descrição vazia")

    assert rigging.pose_por_texto("   ", OSSOS, NuncaChamado()) == {}
