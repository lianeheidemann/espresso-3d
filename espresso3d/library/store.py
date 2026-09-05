"""Biblioteca dos modelos gerados.

O sistema de arquivos é a fonte da verdade: a lista vem de varrer
``outputs/*/meta.json``. Não existe banco de dados para dessincronizar —
o usuário pode mover, copiar ou apagar pastas por fora que nada quebra.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

RAIZ = Path("outputs")
META = "meta.json"


@dataclass
class Item:
    """Um modelo gerado, montado a partir do meta.json da pasta."""

    pasta: Path
    nome: str
    criado_em: str
    motor: str
    faces: int
    formatos: list[str]
    partes: int
    bytes: int
    avisos: list[str]

    @property
    def mb(self) -> float:
        return round(self.bytes / (1024 * 1024), 1)

    @property
    def preview(self) -> Path | None:
        for candidato in sorted(self.pasta.glob("*.glb")):
            return candidato
        return None

    @property
    def imagem_origem(self) -> Path | None:
        origem = self.pasta / "source.png"
        return origem if origem.exists() else None


def registrar(resultado, cfg, nome: str) -> Path:
    """Escreve o ``meta.json`` que faz a pasta aparecer na biblioteca."""
    meta = {
        "nome": nome,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "motor": cfg.engine,
        "faces": resultado.estatisticas.get("faces", 0),
        "formatos": sorted({a.suffix.lstrip(".") for a in resultado.arquivos}),
        "partes": resultado.partes,
        "duracao_s": resultado.duracao_s,
        "avisos": resultado.avisos,
        "config": cfg.como_dict(),
    }
    caminho = Path(resultado.pasta) / META
    caminho.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return caminho


def listar(raiz: Path = RAIZ) -> list[Item]:
    """Todos os modelos, do mais novo para o mais antigo."""
    raiz = Path(raiz)
    if not raiz.exists():
        return []

    itens: list[Item] = []
    for pasta in sorted(raiz.iterdir(), reverse=True):
        if not pasta.is_dir():
            continue
        item = _ler(pasta)
        if item is not None:
            itens.append(item)
    return itens


def _ler(pasta: Path) -> Item | None:
    caminho = pasta / META
    if not caminho.exists():
        return None
    try:
        meta = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("meta.json ilegível em %s: %s", pasta, exc)
        return None

    return Item(
        pasta=pasta,
        nome=meta.get("nome", pasta.name),
        criado_em=meta.get("criado_em", ""),
        motor=meta.get("motor", "?"),
        faces=int(meta.get("faces", 0) or 0),
        formatos=list(meta.get("formatos", [])),
        partes=int(meta.get("partes", 1) or 1),
        bytes=tamanho(pasta),
        avisos=list(meta.get("avisos", [])),
    )


def tamanho(pasta: Path) -> int:
    """Bytes ocupados por uma pasta de modelo."""
    return sum(f.stat().st_size for f in Path(pasta).rglob("*") if f.is_file())


def espaco_total(raiz: Path = RAIZ) -> tuple[int, int]:
    """(quantidade de modelos, bytes no disco)."""
    itens = listar(raiz)
    return len(itens), sum(i.bytes for i in itens)


def apagar(pasta: Path, para_lixeira: bool = True) -> bool:
    """Remove uma pasta de modelo.

    Por padrão manda para a lixeira do sistema, que é recuperável.
    Apagar arquivo de usuário sem volta é coisa que só se faz quando a
    pessoa pede explicitamente.
    """
    pasta = Path(pasta)
    if not pasta.exists():
        return False

    if para_lixeira:
        try:
            from send2trash import send2trash

            send2trash(str(pasta))
            return True
        except ImportError:
            log.warning(
                "send2trash não instalado — apagando definitivamente. "
                "Instale com: pip install send2trash"
            )
        except Exception as exc:
            log.warning("Lixeira indisponível (%s) — apagando definitivamente.", exc)

    shutil.rmtree(pasta)
    return True


def apagar_varios(pastas: list[Path], para_lixeira: bool = True) -> int:
    return sum(1 for p in pastas if apagar(p, para_lixeira))
