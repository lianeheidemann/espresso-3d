"""Discovery of what the machine has: GPU, Blender and Ollama.

Everything here degrades silently: if the dependency doesn't exist, the
function returns ``None`` or an empty list instead of blowing up. The UI
uses this to disable options with an explanation, instead of erroring out
at generation time.
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

#: Paths where Blender usually lives when it's not on the PATH.
_LIKELY_BLENDER_PATHS = [
    "/usr/bin/blender",
    "/usr/local/bin/blender",
    "/snap/bin/blender",
    "/Applications/Blender.app/Contents/MacOS/Blender",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
]


@functools.lru_cache(maxsize=1)
def vram_gb() -> float | None:
    """GPU VRAM in GB, or ``None`` if there's no usable CUDA GPU."""
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
def gpu_name() -> str | None:
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except Exception:
        pass
    return None


@functools.lru_cache(maxsize=1)
def blender() -> str | None:
    """Path to the Blender executable, or ``None``."""
    if env := os.environ.get("BLENDER_BIN"):
        if Path(env).exists():
            return env
    if found := shutil.which("blender"):
        return found
    for path in _LIKELY_BLENDER_PATHS:
        if Path(path).exists():
            return path
    return None


def blender_version() -> str | None:
    exe = blender()
    if not exe:
        return None
    try:
        output = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=20
        ).stdout
        first_line = output.strip().splitlines()[0] if output.strip() else ""
        return first_line or None
    except Exception:
        return None


def ollama_running() -> bool:
    return ollama_models() is not None


def ollama_models() -> list[str] | None:
    """Models already downloaded in Ollama.

    ``None`` means "Ollama isn't running"; an empty list means "it's
    running, but with no model downloaded" — these are different
    situations and the UI shows a different message for each.
    """
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as resp:
            data = json.loads(resp.read().decode())
        return [m["name"] for m in data.get("models", [])]
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return None


def summary() -> dict:
    """A one-line status for the UI header."""
    vram = vram_gb()
    models = ollama_models()
    return {
        "gpu": gpu_name(),
        "vram_gb": vram,
        "blender": blender(),
        "blender_version": blender_version(),
        "ollama": models is not None,
        "ollama_models": models or [],
    }


def summary_text() -> str:
    """Short hardware summary, the way it appears at the top of the screen."""
    r = summary()
    parts = []
    if r["vram_gb"]:
        parts.append(f"GPU: {r['vram_gb']:g} GB VRAM")
    else:
        parts.append("No CUDA GPU — will run on CPU (much slower)")
    parts.append("Blender: found" if r["blender"] else "Blender: not found")
    if r["ollama"]:
        parts.append(f"Ollama: {len(r['ollama_models'])} model(s)")
    else:
        parts.append("Ollama: off")
    return " · ".join(parts)
