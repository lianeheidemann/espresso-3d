"""Natural-language request → :class:`PipelineConfig`.

Two paths, same output: the LLM returns JSON, or basic mode looks for
known words. Either way, the result is always shown on the confirmation
card before running — the agent never generates anything without the
user approving what it understood.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import replace

from ..config import FORMATS, License, PipelineConfig, Pose, TextureResolution, Topology

log = logging.getLogger(__name__)

PROMPT = """You configure a 3D model generator from images.

User request: "{request}"

Respond with ONLY a JSON object containing the keys the request mentions:
- "engine": "tripo_sr" (fast), "stable_fast_3d" (balanced) or "instant_mesh" (max quality)
- "poly_count_target": integer between 500 and 20000
- "generate_texture": true/false
- "texture_resolution": "standard" or "ultra_2k"
- "pose": "none", "t_pose", "a_pose" or "custom"
- "pose_prompt": pose description, if any
- "split_parts": true/false (separate objects)
- "enhance_image": true/false
- "license": "private" or "commercial"
- "formats": list from among {formats}

Omit whatever the request doesn't say. Don't make up values."""

#: Words that basic mode recognizes, with no LLM at all.
_HIGH_QUALITY = ("high quality", "highest", "maximum", "detailed", "fancy")
_FAST_QUALITY = ("fast", "quick", "simple", "light", "draft")
_SPLIT = ("separate", "split", "divided", "parts", "pieces")
_NO_TEXTURE = ("no texture", "no color", "mesh only", "just the mesh", "without texture")


def do_llm(request: str, backend, base: PipelineConfig | None = None) -> PipelineConfig:
    """Uses the LLM. If it fails or returns garbage, falls back to basic mode."""
    base = base or PipelineConfig()
    try:
        response = backend.complete(
            PROMPT.format(request=request, formats=", ".join(sorted(FORMATS)))
        )
        data = _extract_json(response)
    except Exception as exc:
        log.info("LLM unavailable (%s) — using basic mode.", exc)
        return by_keywords(request, base)

    if not data:
        return by_keywords(request, base)
    return apply(data, base)


def apply(data: dict, base: PipelineConfig) -> PipelineConfig:
    """Applies a dict to the configuration, ignoring whatever is invalid.

    Never raises an exception because of a weird field: the user sees
    the confirmation card and corrects by hand whatever the model got
    wrong.
    """
    cfg = replace(base)

    if isinstance(data.get("engine"), str):
        from ..engines import ENGINES

        if data["engine"] in ENGINES:
            cfg.engine = data["engine"]

    if isinstance(data.get("poly_count_target"), (int, float)):
        cfg.poly_count_target = max(500, min(20_000, int(data["poly_count_target"])))

    for field in ("generate_texture", "split_parts", "enhance_image"):
        if isinstance(data.get(field), bool):
            setattr(cfg, field, data[field])

    cfg.pose = _enum(data.get("pose"), Pose, cfg.pose)
    cfg.license = _enum(data.get("license"), License, cfg.license)
    cfg.topology = _enum(data.get("topology"), Topology, cfg.topology)
    cfg.texture_resolution = _enum(
        data.get("texture_resolution"), TextureResolution, cfg.texture_resolution
    )

    if isinstance(data.get("pose_prompt"), str):
        cfg.pose_prompt = data["pose_prompt"].strip()
        if cfg.pose_prompt and cfg.pose is Pose.NONE:
            cfg.pose = Pose.CUSTOM

    formats = [f for f in data.get("formats", []) if f in FORMATS]
    if formats:
        cfg.formats = formats

    return cfg


def by_keywords(request: str, base: PipelineConfig | None = None) -> PipelineConfig:
    """Interprets without an LLM. Covers the most common requests."""
    cfg = replace(base or PipelineConfig())
    text = request.lower()

    if any(p in text for p in _HIGH_QUALITY):
        cfg.engine = "instant_mesh"
        cfg.texture_resolution = TextureResolution.ULTRA_2K
        cfg.poly_count_target = max(cfg.poly_count_target, 12_000)
    elif any(p in text for p in _FAST_QUALITY):
        cfg.engine = "tripo_sr"
        cfg.poly_count_target = min(cfg.poly_count_target, 4_000)

    if any(p in text for p in _SPLIT):
        cfg.split_parts = True

    if any(p in text for p in _NO_TEXTURE):
        cfg.generate_texture = False

    if "t-pose" in text or "t pose" in text:
        cfg.pose = Pose.T_POSE
    elif "a-pose" in text or "a pose" in text:
        cfg.pose = Pose.A_POSE

    if "commercial" in text:
        cfg.license = License.COMMERCIAL

    if number := re.search(r"(\d[\d,]{2,})\s*(?:polygons|faces|tris)", text):
        raw = int(number.group(1).replace(",", ""))
        cfg.poly_count_target = max(500, min(20_000, raw))

    found = [f for f in FORMATS if f".{f}" in text]
    if found:
        cfg.formats = found

    return cfg


def summary(cfg: PipelineConfig) -> dict[str, str]:
    """What the confirmation card shows before generating."""
    from ..engines import ENGINES

    engine = ENGINES[cfg.engine].info.name if cfg.engine in ENGINES else cfg.engine
    return {
        "Engine": engine,
        "Polygon count": f"{cfg.poly_count_target:,}",
        "Texture": (
            f"Yes · {cfg.texture_resolution.pixels}px" if cfg.generate_texture else "No"
        ),
        "Pose": cfg.pose.value.replace("_", "-"),
        "Split into parts": "Yes" if cfg.split_parts else "No",
        "Enhance image": "Yes" if cfg.enhance_image else "No",
        "License": cfg.license.value,
        "Formats": ", ".join(f".{f}" for f in cfg.formats),
    }


def _enum(value, kind, current):
    if isinstance(value, kind):
        return value
    if isinstance(value, str):
        try:
            return kind(value.strip().lower())
        except ValueError:
            log.debug("Value ignored for %s: %r", kind.__name__, value)
    return current


def _extract_json(text: str) -> dict:
    if not text:
        return {}
    clean = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = clean.find("{"), clean.rfind("}")
    if start == -1 or end <= start:
        return {}
    try:
        data = json.loads(clean[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
