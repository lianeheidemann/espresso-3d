"""Skeleton and pose.

The automatic rig comes from UniRig. The custom pose is translated from
the user's text into bone rotations by the same local LLM that powers
the Agent tab — no extra model download needed.

The LLM's output is never applied raw: it goes through
:func:`validate_rotations`, which discards nonexistent bones and clamps
angles outside the allowed range. A hallucinated JSON becomes, in the
worst case, a partial pose — never a character with an arm rotated 900°.
"""

from __future__ import annotations

import json
import logging
import re

from ..config import Pose

log = logging.getLogger(__name__)

#: Limit per axis, in degrees. No human joint goes past this.
DEGREE_LIMIT = 180.0

#: Bones of a standard humanoid rig (simplified Mixamo/UniRig naming).
HUMANOID_BONES = [
    "hips", "spine", "chest", "neck", "head",
    "left_shoulder", "left_upper_arm", "left_lower_arm", "left_hand",
    "right_shoulder", "right_upper_arm", "right_lower_arm", "right_hand",
    "left_upper_leg", "left_lower_leg", "left_foot",
    "right_upper_leg", "right_lower_leg", "right_foot",
]

_PROMPT = """You convert pose descriptions into bone rotations.

Bones available in this skeleton:
{bones}

Pose description: "{description}"

Respond with ONLY a JSON object mapping bone name to [x, y, z] in degrees.
Use only bones from the list. Omit bones that don't change.
Example: {{"right_upper_arm": [0, 0, -75], "head": [0, 25, 0]}}"""


class RigUnavailable(RuntimeError):
    """Raised when there's no humanoid skeleton to pose."""


def validate_rotations(raw: dict, valid_bones: list[str]) -> dict[str, list[float]]:
    """Filters and clamps what the LLM returned.

    An unknown bone is discarded (with a log entry), a non-numeric value
    is discarded, an out-of-range angle is clamped. What's left is safe
    to apply.
    """
    valid = set(valid_bones)
    clean: dict[str, list[float]] = {}

    for bone, angles in (raw or {}).items():
        key = str(bone).strip().lower().replace(" ", "_").replace("-", "_")
        if key not in valid:
            log.debug("Bone ignored (doesn't exist in this rig): %s", bone)
            continue
        if not isinstance(angles, (list, tuple)) or len(angles) != 3:
            log.debug("Rotation ignored (unexpected format) for %s: %r", bone, angles)
            continue
        try:
            axes = [float(a) for a in angles]
        except (TypeError, ValueError):
            log.debug("Rotation ignored (non-numeric value) for %s: %r", bone, angles)
            continue
        clean[key] = [max(-DEGREE_LIMIT, min(DEGREE_LIMIT, a)) for a in axes]

    return clean


def extract_json(text: str) -> dict:
    """Pulls the JSON object out of a response that may have chatter around it.

    Small models like to answer "Sure! Here it is: {...}", and sometimes
    wrap it in a code block.
    """
    if not text:
        return {}
    clean = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    start, end = clean.find("{"), clean.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(clean[start : end + 1])
        except json.JSONDecodeError:
            pass
    log.warning("The LLM's response didn't contain valid JSON.")
    return {}


def pose_from_text(description: str, bones: list[str], backend) -> dict[str, list[float]]:
    """Translates the user's description into validated rotations."""
    if not description.strip():
        return {}
    prompt = _PROMPT.format(bones=", ".join(bones), description=description.strip())
    response = backend.complete(prompt)
    return validate_rotations(extract_json(response), bones)


def pose_from_image(photo_path: str, bones: list[str]) -> dict[str, list[float]]:
    """Copies body angles from a reference photo (MediaPipe)."""
    try:  # pragma: no cover - depends on download
        import mediapipe as mp  # noqa: F401
    except ImportError as exc:
        raise RigUnavailable(
            "To use a reference photo install MediaPipe:\n"
            "  pip install mediapipe"
        ) from exc
    raise RigUnavailable(  # pragma: no cover
        "Pose extraction from a photo isn't implemented yet in this version. "
        "Use the text description."
    )


def apply_rig(mesh, cfg, backend=None):
    """Generates the skeleton and applies the chosen pose.

    Without UniRig installed, returns the mesh without a rig and
    explains what's missing — it doesn't block the whole generation
    because of the pose.
    """
    if cfg.pose is Pose.NONE:
        return mesh, None

    try:  # pragma: no cover - depends on download
        import unirig  # type: ignore  # noqa: F401
    except ImportError as exc:
        raise RigUnavailable(
            "Pose and skeleton need UniRig:\n"
            "  git clone https://github.com/VAST-AI-Research/UniRig\n"
            "  pip install -e UniRig\n"
            "The model is generated normally without a rig if you choose Pose: None."
        ) from exc

    raise RigUnavailable(  # pragma: no cover
        "UniRig found, but rig integration isn't complete yet in this version."
    )
