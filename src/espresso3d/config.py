"""Configuration for a single generation.

A single :class:`PipelineConfig` instance is shared by the "Image → 3D"
and "Batch" tabs: the batch tab has no panel of its own, it inherits
whatever is configured on the single-image tab.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class Topology(str, Enum):
    """How the mesh is reduced down to the target polygon count."""

    HIGH_DETAIL = "high_detail"
    SMART = "smart_topology"


class Pose(str, Enum):
    NONE = "none"
    T_POSE = "t_pose"
    A_POSE = "a_pose"
    CUSTOM = "custom"


class License(str, Enum):
    PRIVATE = "private"
    COMMERCIAL = "commercial"


class TextureResolution(str, Enum):
    STANDARD = "standard"
    ULTRA_2K = "ultra_2k"

    @property
    def pixels(self) -> int:
        return 1024 if self is TextureResolution.STANDARD else 2048


@dataclass(frozen=True)
class Format:
    """An export format and what it's able to carry."""

    ext: str
    group: str
    backend: str  # "trimesh" (pure Python) or "blender" (headless script)
    supports_rig: bool
    supports_texture: bool
    note: str = ""


#: Format catalog, grouped by where the model is going — not by extension.
FORMATS: dict[str, Format] = {
    "glb": Format("glb", "Web and Android AR", "trimesh", True, True, "AR Web"),
    "gltf": Format("gltf", "Web and Android AR", "trimesh", True, True),
    "usdz": Format("usdz", "iPhone / Vision Pro AR", "blender", True, True, "AR iOS"),
    "usdc": Format("usdc", "USD / Omniverse pipelines", "blender", True, True),
    "usda": Format("usda", "USD / Omniverse pipelines", "blender", True, True),
    "fbx": Format("fbx", "Unity / Unreal / VR", "blender", True, True),
    "vrm": Format("vrm", "Unity / Unreal / VR", "blender", True, True, "avatar · beta"),
    "obj": Format("obj", "Editing and general use", "trimesh", False, True, "zipped with .mtl"),
    "ply": Format("ply", "Editing and general use", "trimesh", False, False),
    "dae": Format("dae", "Editing and general use", "blender", True, True),
    "blend": Format("blend", "Editing and general use", "blender", True, True),
    "stl": Format("stl", "3D printing", "trimesh", False, False),
    "3mf": Format("3mf", "3D printing", "trimesh", False, True),
}

POLY_MIN, POLY_MAX = 500, 20_000
MAX_BATCH_IMAGES = 10


@dataclass
class PipelineConfig:
    """Everything the user chooses before generating."""

    engine: str = "stable_fast_3d"
    topology: Topology = Topology.HIGH_DETAIL
    poly_count_target: int = 4000
    generate_texture: bool = True
    texture_resolution: TextureResolution = TextureResolution.STANDARD
    pose: Pose = Pose.NONE
    pose_prompt: str = ""
    pose_ref_image: str | None = None
    split_parts: bool = False
    enhance_image: bool = True
    license: License = License.PRIVATE
    formats: list[str] = field(default_factory=lambda: ["glb"])

    # ------------------------------------------------------------------ #

    def validate(self) -> None:
        """Raises ``ValueError`` with a message the user can understand."""
        if not self.formats:
            raise ValueError("Choose at least one export format.")

        unknown = [f for f in self.formats if f not in FORMATS]
        if unknown:
            raise ValueError(f"Unknown format: {', '.join(unknown)}")

        if not POLY_MIN <= self.poly_count_target <= POLY_MAX:
            raise ValueError(
                f"Polygon count must be between {POLY_MIN} and {POLY_MAX:,}."
            )

        if self.pose is Pose.CUSTOM and not (self.pose_prompt.strip() or self.pose_ref_image):
            raise ValueError(
                "Custom pose needs either a text description "
                "or a reference photo."
            )

    def warnings(self) -> list[str]:
        """Losses the user needs to know about BEFORE generating.

        Better to warn while configuring than to hand over a file without
        texture and let the person find out on their own in Blender.
        """
        warnings: list[str] = []
        chosen = [FORMATS[f] for f in self.formats if f in FORMATS]

        if self.generate_texture:
            no_texture = [f.ext for f in chosen if not f.supports_texture]
            if no_texture:
                warnings.append(
                    f".{', .'.join(no_texture)} doesn't store texture or color."
                )

        if self.pose is not Pose.NONE:
            no_rig = [f.ext for f in chosen if not f.supports_rig]
            if no_rig:
                warnings.append(
                    f".{', .'.join(no_rig)} doesn't carry a skeleton — "
                    "the rig will be discarded in these files."
                )

        if "obj" in self.formats:
            warnings.append(".obj comes out zipped together with .mtl and the textures.")

        return warnings

    @property
    def needs_blender(self) -> list[str]:
        """Chosen formats that only come out with Blender installed."""
        return [f for f in self.formats if FORMATS[f].backend == "blender"]

    @property
    def needs_rig(self) -> bool:
        return self.pose is not Pose.NONE

    def to_dict(self) -> dict:
        d = asdict(self)
        for key in ("topology", "pose", "license", "texture_resolution"):
            d[key] = getattr(self, key).value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "PipelineConfig":
        d = dict(d)
        conversions = {
            "topology": Topology,
            "pose": Pose,
            "license": License,
            "texture_resolution": TextureResolution,
        }
        for key, kind in conversions.items():
            if key in d and not isinstance(d[key], kind):
                d[key] = kind(d[key])
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})


def formats_by_group() -> dict[str, list[Format]]:
    """Formats grouped by destination, in the order they appear in the UI."""
    groups: dict[str, list[Format]] = {}
    for fmt in FORMATS.values():
        groups.setdefault(fmt.group, []).append(fmt)
    return groups
