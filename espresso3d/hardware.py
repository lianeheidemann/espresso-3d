"""Descoberta do que a máquina tem: GPU, Blender e Ollama.

Tudo aqui degrada em silêncio: se a dependência não existe, a função
devolve ``None`` ou lista vazia em vez de explodir. A interface usa isso
para desabilitar opções com explicação, em vez de dar erro na hora de gerar.
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

#: Caminhos onde o Blender costuma estar quando não está no PATH.
_BLENDER_PROVAVEIS = [
    "/usr/bin/blender",
    "/usr/local/bin/blender",
    "/snap/bin/blender",
    "/Applications/Blender.app/Contents/MacOS/Blender",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
]


@functools.lru_cache(maxsize=1)
def vram_gb() -> float | None:
    """VRAM da GPU em GB, ou ``None`` se não houver GPU CUDA utilizável."""
    try:
        import torch
    except ImportError:
        return None
    try:
        if not torch.cuda.is_available():
            return None
        props = torch.cuda.get_device_properties(0)
        return round(props.total_memory / (1024**3), 1)
    except Exception:
        return None


@functools.lru_cache(maxsize=1)
def nome_gpu() -> str | None:
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except Exception:
        pass
    return None


@functools.lru_cache(maxsize=1)
def blender() -> str | None:
    """Caminho do executável do Blender, ou ``None``."""
    if env := os.environ.get("BLENDER_BIN"):
        if Path(env).exists():
            return env
    if achado := shutil.which("blender"):
        return achado
    for caminho in _BLENDER_PROVAVEIS:
        if Path(caminho).exists():
            return caminho
    return None


def versao_blender() -> str | None:
    exe = blender()
    if not exe:
        return None
    try:
        saida = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=20
        ).stdout
        primeira = saida.strip().splitlines()[0] if saida.strip() else ""
        return primeira or None
    except Exception:
        return None


def ollama_ligado() -> bool:
    return ollama_modelos() is not None


def ollama_modelos() -> list[str] | None:
    """Modelos já baixados no Ollama.

    ``None`` significa "Ollama não está rodando"; lista vazia significa
    "está rodando, mas sem modelo baixado" — são situações diferentes e a
    interface mostra mensagens diferentes para cada uma.
    """
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as resp:
            dados = json.loads(resp.read().decode())
        return [m["name"] for m in dados.get("models", [])]
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return None


def resumo() -> dict:
    """Uma linha de status para o cabeçalho da interface."""
    vram = vram_gb()
    modelos = ollama_modelos()
    return {
        "gpu": nome_gpu(),
        "vram_gb": vram,
        "blender": blender(),
        "versao_blender": versao_blender(),
        "ollama": modelos is not None,
        "modelos_ollama": modelos or [],
    }


def texto_resumo() -> str:
    """Resumo curto do hardware, do jeito que aparece no topo da tela."""
    r = resumo()
    partes = []
    if r["vram_gb"]:
        partes.append(f"GPU: {r['vram_gb']:g} GB VRAM")
    else:
        partes.append("Sem GPU CUDA — vai rodar na CPU (bem mais lento)")
    partes.append("Blender: encontrado" if r["blender"] else "Blender: não encontrado")
    if r["ollama"]:
        partes.append(f"Ollama: {len(r['modelos_ollama'])} modelo(s)")
    else:
        partes.append("Ollama: desligado")
    return " · ".join(partes)
