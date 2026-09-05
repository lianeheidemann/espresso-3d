"""Agent brains: local Ollama, free cloud, and the no-LLM fallback.

All of them implement ``complete(prompt) -> str``. The registry describes
what each one costs to download and whether it can see images, and the UI
uses this to show the install command instead of an error.
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
class BrainInfo:
    id: str
    name: str
    size: str
    fits: str
    vision: bool
    local: bool
    install: str = ""


class Brain:
    info: BrainInfo

    def available(self) -> bool:
        raise NotImplementedError

    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class Ollama(Brain):
    """Model running on the machine, via Ollama. Offline and with no usage limit."""

    def __init__(self, info: BrainInfo):
        self.info = info
        self.url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    def available(self) -> bool:
        from ..hardware import ollama_models

        models = ollama_models()
        if models is None:
            return False
        return any(m.split(":")[0] == self.info.id.split(":")[0] for m in models)

    def complete(self, prompt: str, cpu: bool = True) -> str:
        body = json.dumps(
            {
                "model": self.info.id,
                "prompt": prompt,
                "stream": False,
                # num_gpu=0 keeps the LLM on the CPU and leaves the whole
                # VRAM budget for the 3D generator, which is where it's needed.
                "options": {"temperature": 0.2, **({"num_gpu": 0} if cpu else {})},
            }
        ).encode()

        req = urllib.request.Request(
            f"{self.url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode()).get("response", "")
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Ollama didn't respond at {self.url}.\n"
                "Start it with 'ollama serve' and download the model with "
                f"'ollama pull {self.info.id}'."
            ) from exc


class Cloud(Brain):
    """Service with a free tier. Needs an API key and internet."""

    def __init__(self, info: BrainInfo, env_key: str, url: str, model: str):
        self.info = info
        self.env_key = env_key
        self.url = url
        self.model = model

    def available(self) -> bool:
        return bool(os.environ.get(self.env_key))

    def complete(self, prompt: str) -> str:
        key = os.environ.get(self.env_key)
        if not key:
            raise RuntimeError(
                f"Set {self.env_key} in the environment (or in a .env file) "
                f"to use {self.info.name}."
            )
        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
        ).encode()
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"]


class Keywords(Brain):
    """No-LLM-at-all fallback.

    Exists so the Agent tab never breaks just because the person hasn't
    downloaded a model. Interprets the request through known keywords.
    """

    info = BrainInfo(
        id="keywords",
        name="Basic mode (keywords)",
        size="nothing to download",
        fits="uses no GPU or internet",
        vision=False,
        local=True,
    )

    def available(self) -> bool:
        return True

    def complete(self, prompt: str) -> str:
        # With no LLM there's no free text to generate; the caller uses
        # the keyword parser directly instead.
        return ""


BRAINS: dict[str, Brain] = {}


def _register(brain: Brain) -> None:
    BRAINS[brain.info.id] = brain


for _info in [
    BrainInfo("gemma3:4b", "Gemma 3 4B", "3.3 GB", "any GPU, or CPU", True, True,
              "ollama pull gemma3:4b"),
    BrainInfo("qwen2.5:3b", "Qwen 2.5 3B", "2.0 GB", "any GPU, or CPU", False, True,
              "ollama pull qwen2.5:3b"),
    BrainInfo("qwen2.5:7b", "Qwen 2.5 7B", "4.7 GB", "8GB VRAM or CPU", False, True,
              "ollama pull qwen2.5:7b"),
    BrainInfo("llama3.1:8b", "Llama 3.1 8B", "4.9 GB", "8GB VRAM or CPU", False, True,
              "ollama pull llama3.1:8b"),
    BrainInfo("mistral:7b", "Mistral 7B", "4.4 GB", "6GB VRAM or CPU", False, True,
              "ollama pull mistral:7b"),
    BrainInfo("moondream", "Moondream 2B", "1.7 GB", "any GPU, or CPU", True, True,
               "ollama pull moondream"),
]:
    _register(Ollama(_info))

_register(
    Cloud(
        BrainInfo("groq", "Groq (free tier)", "no download",
                  "needs a key and internet", False, False,
                  "export GROQ_API_KEY=..."),
        "GROQ_API_KEY",
        "https://api.groq.com/openai/v1/chat/completions",
        "llama-3.1-8b-instant",
    )
)
_register(
    Cloud(
        BrainInfo("openrouter", "OpenRouter (:free models)", "no download",
                  "needs a key and internet", False, False,
                  "export OPENROUTER_API_KEY=..."),
        "OPENROUTER_API_KEY",
        "https://openrouter.ai/api/v1/chat/completions",
        "meta-llama/llama-3.1-8b-instruct:free",
    )
)
_register(Keywords())


def get(brain_id: str) -> Brain:
    if brain_id not in BRAINS:
        raise KeyError(f"Brain '{brain_id}' doesn't exist.")
    return BRAINS[brain_id]


def default() -> Brain:
    """The first genuinely usable brain, in order of preference."""
    for brain in BRAINS.values():
        if brain.info.local and brain.available():
            return brain
    return BRAINS["keywords"]
