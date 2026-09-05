"""Cérebros do agente: Ollama local, nuvem grátis e o plano B sem LLM.

Todos implementam ``completar(prompt) -> str``. O registro descreve o que
cada um custa em download e se enxerga imagem, e a interface usa isso para
mostrar o comando de instalação em vez de um erro.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class InfoCerebro:
    id: str
    nome: str
    tamanho: str
    onde_cabe: str
    visao: bool
    local: bool
    instalar: str = ""


class Cerebro:
    info: InfoCerebro

    def disponivel(self) -> bool:
        raise NotImplementedError

    def completar(self, prompt: str) -> str:
        raise NotImplementedError


class Ollama(Cerebro):
    """Modelo rodando na máquina, via Ollama. Offline e sem limite de uso."""

    def __init__(self, info: InfoCerebro):
        self.info = info
        self.url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    def disponivel(self) -> bool:
        from ..hardware import ollama_modelos

        modelos = ollama_modelos()
        if modelos is None:
            return False
        return any(m.split(":")[0] == self.info.id.split(":")[0] for m in modelos)

    def completar(self, prompt: str, cpu: bool = True) -> str:
        corpo = json.dumps(
            {
                "model": self.info.id,
                "prompt": prompt,
                "stream": False,
                # num_gpu=0 mantém o LLM na CPU e deixa a VRAM inteira
                # para o gerador 3D, que é onde ela faz falta.
                "options": {"temperature": 0.2, **({"num_gpu": 0} if cpu else {})},
            }
        ).encode()

        req = urllib.request.Request(
            f"{self.url}/api/generate",
            data=corpo,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode()).get("response", "")
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Ollama não respondeu em {self.url}.\n"
                "Inicie com 'ollama serve' e baixe o modelo com "
                f"'ollama pull {self.info.id}'."
            ) from exc


class Nuvem(Cerebro):
    """Serviço com plano gratuito. Precisa de chave e internet."""

    def __init__(self, info: InfoCerebro, env_chave: str, url: str, modelo: str):
        self.info = info
        self.env_chave = env_chave
        self.url = url
        self.modelo = modelo

    def disponivel(self) -> bool:
        return bool(os.environ.get(self.env_chave))

    def completar(self, prompt: str) -> str:
        chave = os.environ.get(self.env_chave)
        if not chave:
            raise RuntimeError(
                f"Defina {self.env_chave} no ambiente (ou num arquivo .env) "
                f"para usar {self.info.nome}."
            )
        corpo = json.dumps(
            {
                "model": self.modelo,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
        ).encode()
        req = urllib.request.Request(
            self.url,
            data=corpo,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {chave}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            dados = json.loads(resp.read().decode())
        return dados["choices"][0]["message"]["content"]


class PalavrasChave(Cerebro):
    """Plano B sem LLM nenhum.

    Existe para a aba Agente nunca ficar quebrada só porque a pessoa não
    baixou um modelo. Interpreta o pedido por palavras conhecidas.
    """

    info = InfoCerebro(
        id="palavras_chave",
        nome="Modo básico (palavras-chave)",
        tamanho="nada para baixar",
        onde_cabe="não usa GPU nem internet",
        visao=False,
        local=True,
    )

    def disponivel(self) -> bool:
        return True

    def completar(self, prompt: str) -> str:
        # Sem LLM não há texto livre para gerar; quem chama usa o parser
        # por palavras-chave diretamente.
        return ""


CEREBROS: dict[str, Cerebro] = {}


def _registrar(cerebro: Cerebro) -> None:
    CEREBROS[cerebro.info.id] = cerebro


for _info in [
    InfoCerebro("gemma3:4b", "Gemma 3 4B", "3,3 GB", "qualquer GPU, ou CPU", True, True,
                "ollama pull gemma3:4b"),
    InfoCerebro("qwen2.5:3b", "Qwen 2.5 3B", "2,0 GB", "qualquer GPU, ou CPU", False, True,
                "ollama pull qwen2.5:3b"),
    InfoCerebro("qwen2.5:7b", "Qwen 2.5 7B", "4,7 GB", "8GB VRAM ou CPU", False, True,
                "ollama pull qwen2.5:7b"),
    InfoCerebro("llama3.1:8b", "Llama 3.1 8B", "4,9 GB", "8GB VRAM ou CPU", False, True,
                "ollama pull llama3.1:8b"),
    InfoCerebro("mistral:7b", "Mistral 7B", "4,4 GB", "6GB VRAM ou CPU", False, True,
                "ollama pull mistral:7b"),
    InfoCerebro("moondream", "Moondream 2B", "1,7 GB", "qualquer GPU, ou CPU", True, True,
                "ollama pull moondream"),
]:
    _registrar(Ollama(_info))

_registrar(
    Nuvem(
        InfoCerebro("groq", "Groq (plano gratuito)", "sem download",
                    "precisa de chave e internet", False, False,
                    "export GROQ_API_KEY=..."),
        "GROQ_API_KEY",
        "https://api.groq.com/openai/v1/chat/completions",
        "llama-3.1-8b-instant",
    )
)
_registrar(
    Nuvem(
        InfoCerebro("openrouter", "OpenRouter (modelos :free)", "sem download",
                    "precisa de chave e internet", False, False,
                    "export OPENROUTER_API_KEY=..."),
        "OPENROUTER_API_KEY",
        "https://openrouter.ai/api/v1/chat/completions",
        "meta-llama/llama-3.1-8b-instruct:free",
    )
)
_registrar(PalavrasChave())


def obter(id_cerebro: str) -> Cerebro:
    if id_cerebro not in CEREBROS:
        raise KeyError(f"Cérebro '{id_cerebro}' não existe.")
    return CEREBROS[id_cerebro]


def padrao() -> Cerebro:
    """O primeiro cérebro realmente utilizável, na ordem de preferência."""
    for cerebro in CEREBROS.values():
        if cerebro.info.local and cerebro.disponivel():
            return cerebro
    return CEREBROS["palavras_chave"]
