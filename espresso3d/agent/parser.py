"""Pedido em português → :class:`PipelineConfig`.

Dois caminhos, mesma saída: o LLM devolve JSON, ou o modo básico procura
palavras conhecidas. Em ambos, o resultado é sempre mostrado no card de
confirmação antes de rodar — o agente nunca gera nada sem o usuário
aprovar o que ele entendeu.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import replace

from ..config import FORMATOS, Licenca, PipelineConfig, Pose, ResolucaoTextura, Topologia

log = logging.getLogger(__name__)

PROMPT = """Você configura um gerador de modelos 3D a partir de imagens.

Pedido do usuário: "{pedido}"

Responda APENAS um objeto JSON com as chaves que o pedido mencionar:
- "engine": "tripo_sr" (rápido), "stable_fast_3d" (equilíbrio) ou "instant_mesh" (máxima qualidade)
- "poly_count_alvo": inteiro entre 500 e 20000
- "gerar_textura": true/false
- "resolucao_textura": "padrao" ou "ultra_2k"
- "pose": "nenhum", "t_pose", "a_pose" ou "customizada"
- "pose_prompt": descrição da pose, se houver
- "dividir_partes": true/false (objetos separados)
- "melhorar_imagem": true/false
- "licenca": "privada" ou "comercial"
- "formatos": lista entre {formatos}

Omita o que o pedido não disser. Não invente valores."""

#: Palavras que o modo básico reconhece, sem LLM nenhum.
_QUALIDADE_ALTA = ("alta qualidade", "máxima", "maxima", "detalhad", "caprichad")
_QUALIDADE_RAPIDA = ("rápido", "rapido", "simples", "leve", "rascunho")
_DIVIDIR = ("separad", "dividir", "dividid", "partes", "peças", "pecas")
_SEM_TEXTURA = ("sem textura", "sem cor", "só malha", "so malha", "apenas a malha")


def do_llm(pedido: str, backend, base: PipelineConfig | None = None) -> PipelineConfig:
    """Usa o LLM. Se ele falhar ou devolver lixo, cai no modo básico."""
    base = base or PipelineConfig()
    try:
        resposta = backend.completar(
            PROMPT.format(pedido=pedido, formatos=", ".join(sorted(FORMATOS)))
        )
        dados = _extrair_json(resposta)
    except Exception as exc:
        log.info("LLM indisponível (%s) — usando o modo básico.", exc)
        return por_palavras_chave(pedido, base)

    if not dados:
        return por_palavras_chave(pedido, base)
    return aplicar(dados, base)


def aplicar(dados: dict, base: PipelineConfig) -> PipelineConfig:
    """Aplica um dicionário à configuração, ignorando o que for inválido.

    Nunca levanta exceção por causa de um campo estranho: o usuário vê o
    card de confirmação e corrige na mão o que o modelo errou.
    """
    cfg = replace(base)

    if isinstance(dados.get("engine"), str):
        from ..engines import MOTORES

        if dados["engine"] in MOTORES:
            cfg.engine = dados["engine"]

    if isinstance(dados.get("poly_count_alvo"), (int, float)):
        cfg.poly_count_alvo = max(500, min(20_000, int(dados["poly_count_alvo"])))

    for campo in ("gerar_textura", "dividir_partes", "melhorar_imagem"):
        if isinstance(dados.get(campo), bool):
            setattr(cfg, campo, dados[campo])

    cfg.pose = _enum(dados.get("pose"), Pose, cfg.pose)
    cfg.licenca = _enum(dados.get("licenca"), Licenca, cfg.licenca)
    cfg.topologia = _enum(dados.get("topologia"), Topologia, cfg.topologia)
    cfg.resolucao_textura = _enum(
        dados.get("resolucao_textura"), ResolucaoTextura, cfg.resolucao_textura
    )

    if isinstance(dados.get("pose_prompt"), str):
        cfg.pose_prompt = dados["pose_prompt"].strip()
        if cfg.pose_prompt and cfg.pose is Pose.NENHUM:
            cfg.pose = Pose.CUSTOM

    formatos = [f for f in dados.get("formatos", []) if f in FORMATOS]
    if formatos:
        cfg.formatos = formatos

    return cfg


def por_palavras_chave(pedido: str, base: PipelineConfig | None = None) -> PipelineConfig:
    """Interpreta sem LLM. Cobre os pedidos mais comuns."""
    cfg = replace(base or PipelineConfig())
    texto = pedido.lower()

    if any(p in texto for p in _QUALIDADE_ALTA):
        cfg.engine = "instant_mesh"
        cfg.resolucao_textura = ResolucaoTextura.ULTRA_2K
        cfg.poly_count_alvo = max(cfg.poly_count_alvo, 12_000)
    elif any(p in texto for p in _QUALIDADE_RAPIDA):
        cfg.engine = "tripo_sr"
        cfg.poly_count_alvo = min(cfg.poly_count_alvo, 4_000)

    if any(p in texto for p in _DIVIDIR):
        cfg.dividir_partes = True

    if any(p in texto for p in _SEM_TEXTURA):
        cfg.gerar_textura = False

    if "t-pose" in texto or "t pose" in texto:
        cfg.pose = Pose.T_POSE
    elif "a-pose" in texto or "a pose" in texto:
        cfg.pose = Pose.A_POSE

    if "comercial" in texto:
        cfg.licenca = Licenca.COMERCIAL

    if numero := re.search(r"(\d[\d.]{2,})\s*(?:pol[íi]gonos|faces|tris)", texto):
        bruto = int(numero.group(1).replace(".", ""))
        cfg.poly_count_alvo = max(500, min(20_000, bruto))

    achados = [f for f in FORMATOS if f".{f}" in texto]
    if achados:
        cfg.formatos = achados

    return cfg


def resumo(cfg: PipelineConfig) -> dict[str, str]:
    """O que o card de confirmação mostra antes de gerar."""
    from ..engines import MOTORES

    motor = MOTORES[cfg.engine].info.nome if cfg.engine in MOTORES else cfg.engine
    return {
        "Motor": motor,
        "Contagem de polígonos": f"{cfg.poly_count_alvo:,}".replace(",", "."),
        "Textura": (
            f"Sim · {cfg.resolucao_textura.pixels}px" if cfg.gerar_textura else "Não"
        ),
        "Pose": cfg.pose.value.replace("_", "-"),
        "Dividir em partes": "Sim" if cfg.dividir_partes else "Não",
        "Melhorar imagem": "Sim" if cfg.melhorar_imagem else "Não",
        "Licença": cfg.licenca.value,
        "Formatos": ", ".join(f".{f}" for f in cfg.formatos),
    }


def _enum(valor, tipo, atual):
    if isinstance(valor, tipo):
        return valor
    if isinstance(valor, str):
        try:
            return tipo(valor.strip().lower())
        except ValueError:
            log.debug("Valor ignorado para %s: %r", tipo.__name__, valor)
    return atual


def _extrair_json(texto: str) -> dict:
    if not texto:
        return {}
    limpo = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()
    inicio, fim = limpo.find("{"), limpo.rfind("}")
    if inicio == -1 or fim <= inicio:
        return {}
    try:
        dados = json.loads(limpo[inicio : fim + 1])
    except json.JSONDecodeError:
        return {}
    return dados if isinstance(dados, dict) else {}
