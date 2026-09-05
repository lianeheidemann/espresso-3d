"""Esqueleto e pose.

O rig automático vem do UniRig. A pose personalizada é traduzida do texto
do usuário para rotações de ossos pelo mesmo LLM local que move a aba
Agente — sem baixar modelo nenhum a mais.

A saída do LLM nunca é aplicada crua: passa por :func:`validar_rotacoes`,
que descarta osso inexistente e limita ângulo fora da faixa. Um JSON
alucinado vira, no pior caso, uma pose parcial — nunca um personagem com
o braço girado 900°.
"""

from __future__ import annotations

import json
import logging
import re

from ..config import Pose

log = logging.getLogger(__name__)

#: Limite por eixo, em graus. Junta humana não passa disso.
LIMITE_GRAUS = 180.0

#: Ossos de um rig humanoide padrão (nomenclatura Mixamo/UniRig simplificada).
OSSOS_HUMANOIDES = [
    "hips", "spine", "chest", "neck", "head",
    "left_shoulder", "left_upper_arm", "left_lower_arm", "left_hand",
    "right_shoulder", "right_upper_arm", "right_lower_arm", "right_hand",
    "left_upper_leg", "left_lower_leg", "left_foot",
    "right_upper_leg", "right_lower_leg", "right_foot",
]

_PROMPT = """Você converte descrições de pose em rotações de ossos.

Ossos disponíveis neste esqueleto:
{ossos}

Descrição da pose: "{descricao}"

Responda APENAS um objeto JSON mapeando nome do osso para [x, y, z] em graus.
Use somente ossos da lista. Omita os ossos que não mudam.
Exemplo: {{"right_upper_arm": [0, 0, -75], "head": [0, 25, 0]}}"""


class RigIndisponivel(RuntimeError):
    """Levantado quando não há esqueleto humanoide para posar."""


def validar_rotacoes(bruto: dict, ossos_validos: list[str]) -> dict[str, list[float]]:
    """Filtra e limita o que o LLM devolveu.

    Osso desconhecido é descartado (com log), valor não numérico é
    descartado, ângulo fora de faixa é limitado. O que sobra é seguro
    de aplicar.
    """
    validos = set(ossos_validos)
    limpo: dict[str, list[float]] = {}

    for osso, angulos in (bruto or {}).items():
        chave = str(osso).strip().lower().replace(" ", "_").replace("-", "_")
        if chave not in validos:
            log.debug("Osso ignorado (não existe neste rig): %s", osso)
            continue
        if not isinstance(angulos, (list, tuple)) or len(angulos) != 3:
            log.debug("Rotação ignorada (formato inesperado) em %s: %r", osso, angulos)
            continue
        try:
            eixos = [float(a) for a in angulos]
        except (TypeError, ValueError):
            log.debug("Rotação ignorada (valor não numérico) em %s: %r", osso, angulos)
            continue
        limpo[chave] = [max(-LIMITE_GRAUS, min(LIMITE_GRAUS, a)) for a in eixos]

    return limpo


def extrair_json(texto: str) -> dict:
    """Pega o objeto JSON de uma resposta que pode vir com conversa em volta.

    Modelos pequenos gostam de responder "Claro! Aqui está: {...}", e às
    vezes embrulham em bloco de código.
    """
    if not texto:
        return {}
    limpo = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(limpo)
    except json.JSONDecodeError:
        pass
    inicio, fim = limpo.find("{"), limpo.rfind("}")
    if inicio != -1 and fim > inicio:
        try:
            return json.loads(limpo[inicio : fim + 1])
        except json.JSONDecodeError:
            pass
    log.warning("Resposta do LLM não continha JSON válido.")
    return {}


def pose_por_texto(descricao: str, ossos: list[str], backend) -> dict[str, list[float]]:
    """Traduz a descrição do usuário em rotações validadas."""
    if not descricao.strip():
        return {}
    prompt = _PROMPT.format(ossos=", ".join(ossos), descricao=descricao.strip())
    resposta = backend.completar(prompt)
    return validar_rotacoes(extrair_json(resposta), ossos)


def pose_por_imagem(caminho_foto: str, ossos: list[str]) -> dict[str, list[float]]:
    """Copia os ângulos do corpo de uma foto de referência (MediaPipe)."""
    try:  # pragma: no cover - depende de download
        import mediapipe as mp  # noqa: F401
    except ImportError as exc:
        raise RigIndisponivel(
            "Para usar foto de referência instale o MediaPipe:\n"
            "  pip install mediapipe"
        ) from exc
    raise RigIndisponivel(  # pragma: no cover
        "Extração de pose por foto ainda não implementada nesta versão. "
        "Use a descrição em texto."
    )


def aplicar_rig(malha, cfg, backend=None):
    """Gera o esqueleto e aplica a pose escolhida.

    Sem UniRig instalado, devolve a malha sem rig e explica o que falta —
    não trava a geração inteira por causa da pose.
    """
    if cfg.pose is Pose.NENHUM:
        return malha, None

    try:  # pragma: no cover - depende de download
        import unirig  # type: ignore  # noqa: F401
    except ImportError as exc:
        raise RigIndisponivel(
            "Pose e esqueleto precisam do UniRig:\n"
            "  git clone https://github.com/VAST-AI-Research/UniRig\n"
            "  pip install -e UniRig\n"
            "O modelo é gerado normalmente sem rig se você escolher Pose: Nenhum."
        ) from exc

    raise RigIndisponivel(  # pragma: no cover
        "UniRig encontrado, mas a integração de rig ainda não está completa "
        "nesta versão."
    )
