"""Orquestrador: liga os estágios conforme a configuração escolhida.

    imagem → melhoria → segmentação → geração 3D → malha → rig → exportação

Cada estágio é opcional e falha de forma isolada: se o rig não estiver
disponível, o modelo ainda é gerado e exportado, com o aviso registrado
no resultado.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ..config import PipelineConfig, Pose
from ..engines import obter as obter_motor
from . import enhance, export, mesh_post, rigging, segment

log = logging.getLogger(__name__)

RAIZ_SAIDA = Path("outputs")


@dataclass
class Resultado:
    """O que uma geração produziu — inclusive o que deu errado no caminho."""

    pasta: Path
    arquivos: list[Path] = field(default_factory=list)
    partes: int = 1
    estatisticas: dict = field(default_factory=dict)
    avisos: list[str] = field(default_factory=list)
    duracao_s: float = 0.0

    @property
    def preview(self) -> Path | None:
        """O .glb serve de preview no visualizador da interface."""
        for arquivo in self.arquivos:
            if arquivo.suffix == ".glb":
                return arquivo
        return None


def gerar(
    imagem,
    cfg: PipelineConfig,
    nome: str = "modelo",
    raiz: Path = RAIZ_SAIDA,
    progresso=None,
    backend_llm=None,
) -> Resultado:
    """Roda o pipeline inteiro para uma imagem."""
    cfg.validar()
    inicio = time.monotonic()
    avisos: list[str] = []

    def aviso(passo: str, fracao: float) -> None:
        if progresso is not None:
            progresso(fracao, desc=passo)

    pasta = _criar_pasta(raiz, nome)
    imagem.save(pasta / "source.png")

    if cfg.melhorar_imagem:
        aviso("Melhorando a imagem", 0.1)
        imagem = enhance.melhorar(imagem)

    aviso("Separando as partes" if cfg.dividir_partes else "Preparando", 0.2)
    recortes = segment.separar_objetos(imagem) if cfg.dividir_partes else [imagem]

    motor = obter_motor(cfg.engine)
    malhas = []
    for i, recorte in enumerate(recortes, start=1):
        aviso(f"Gerando 3D ({i}/{len(recortes)})", 0.2 + 0.5 * i / len(recortes))
        malha = motor.gerar(recorte, cfg)
        malha = mesh_post.ajustar_poly_count(malha, cfg.poly_count_alvo, cfg.topologia)
        malhas.append(malha)

    if cfg.pose is not Pose.NENHUM:
        aviso("Aplicando esqueleto e pose", 0.8)
        try:
            malhas = [rigging.aplicar_rig(m, cfg, backend_llm)[0] for m in malhas]
        except rigging.RigIndisponivel as exc:
            avisos.append(f"Sem rig: {exc}")

    aviso("Exportando", 0.9)
    arquivos: list[Path] = []
    for i, malha in enumerate(malhas, start=1):
        sufixo = nome if len(malhas) == 1 else f"{nome}_parte{i}"
        try:
            arquivos += export.exportar(malha, pasta, cfg.formatos, sufixo)
        except export.BlenderNaoEncontrado as exc:
            avisos.append(str(exc))
            somente_leves = [
                f for f in cfg.formatos if f not in cfg.precisa_blender
            ] or ["glb"]
            arquivos += export.exportar(malha, pasta, somente_leves, sufixo)

    avisos += cfg.avisos()
    resultado = Resultado(
        pasta=pasta,
        arquivos=arquivos,
        partes=len(malhas),
        estatisticas=mesh_post.estatisticas(malhas[0]) if malhas else {},
        avisos=avisos,
        duracao_s=round(time.monotonic() - inicio, 1),
    )

    from ..library.store import registrar

    registrar(resultado, cfg, nome)
    return resultado


def gerar_lote(
    imagens: list,
    cfg: PipelineConfig,
    nomes: list[str] | None = None,
    raiz: Path = RAIZ_SAIDA,
    progresso=None,
    backend_llm=None,
) -> list[Resultado]:
    """Roda o pipeline para várias imagens, uma de cada vez.

    Sequencial de propósito: com 4-8GB de VRAM, duas gerações em paralelo
    estouram a memória da GPU e as duas falham.

    Todas usam a MESMA configuração da aba "Imagem → 3D" — o lote não tem
    painel próprio.
    """
    nomes = nomes or [f"modelo_{i + 1}" for i in range(len(imagens))]
    resultados: list[Resultado] = []

    for i, (imagem, nome) in enumerate(zip(imagens, nomes), start=1):
        if progresso is not None:
            progresso((i - 1) / len(imagens), desc=f"Imagem {i} de {len(imagens)}")
        try:
            resultados.append(
                gerar(imagem, cfg, nome=nome, raiz=raiz, backend_llm=backend_llm)
            )
        except Exception as exc:
            log.exception("Falha na imagem %s do lote", i)
            resultados.append(
                Resultado(pasta=raiz / nome, avisos=[f"Falhou: {exc}"])
            )

    return resultados


def _criar_pasta(raiz: Path, nome: str) -> Path:
    carimbo = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    pasta = Path(raiz) / f"{carimbo}_{_limpar_nome(nome)}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _limpar_nome(nome: str) -> str:
    seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in nome.strip())
    return (seguro.strip("_") or "modelo")[:60]
