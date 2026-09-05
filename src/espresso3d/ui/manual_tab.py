""""Image → 3D" and "Batch" tabs.

The batch tab has no options panel: it reads the SAME configuration
from the single-image tab, stored in a shared ``gr.State``. Change it
there, it changes here.
"""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from ..config import (
    FORMATS,
    MAX_BATCH_IMAGES,
    POLY_MAX,
    POLY_MIN,
    License,
    PipelineConfig,
    Pose,
    TextureResolution,
    Topology,
    formats_by_group,
)
from ..engines import ENGINES
from ..hardware import blender as find_blender
from ..pipeline import generate, generate_batch

_POSES = {
    "None": Pose.NONE,
    "T-Pose": Pose.T_POSE,
    "A-Pose": Pose.A_POSE,
    "Custom": Pose.CUSTOM,
}
_TOPOLOGIES = {"High Detail": Topology.HIGH_DETAIL, "Smart Topology": Topology.SMART}
_LICENSES = {"Private": License.PRIVATE, "Commercial": License.COMMERCIAL}
_RESOLUTIONS = {"Standard": TextureResolution.STANDARD, "Ultra 2K": TextureResolution.ULTRA_2K}

POSE_EXAMPLES = [
    "sitting cross-legged",
    "waving with the right hand",
    "running",
    "arms open",
    "crouching",
]


def _format_label(ext: str) -> str:
    fmt = FORMATS[ext]
    marks = []
    if fmt.note:
        marks.append(fmt.note)
    if fmt.backend == "blender":
        marks.append("requires Blender")
    return f".{ext}" + (f"  ({' · '.join(marks)})" if marks else "")


def build(state: gr.State):
    """Assembles the two tabs and returns the components other tabs use."""
    has_blender = find_blender() is not None

    with gr.Tab("Image → 3D"):
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                engine = gr.Radio(
                    choices=[
                        (f"{m.info.name} — {m.info.description} ({m.info.vram_min_gb:g}GB+)",
                         m.info.id)
                        for m in ENGINES.values()
                    ],
                    value="stable_fast_3d",
                    label="Generation engine",
                )
                topology = gr.Radio(
                    choices=list(_TOPOLOGIES), value="High Detail", label="Topology"
                )
                image = gr.Image(
                    label="Image", type="pil", height=220, sources=["upload", "clipboard"]
                )
                poly = gr.Slider(
                    POLY_MIN, POLY_MAX, value=4000, step=100,
                    label="Polygon count",
                )
                texture = gr.Checkbox(value=True, label="Texture")
                resolution = gr.Radio(
                    choices=list(_RESOLUTIONS), value="Standard",
                    label="Texture resolution",
                )
                pose = gr.Radio(choices=list(_POSES), value="None", label="Pose")

                with gr.Group(visible=False) as pose_panel:
                    pose_prompt = gr.Textbox(
                        label="Describe the pose",
                        lines=3,
                        placeholder=(
                            "e.g.: standing, arms crossed over the chest, "
                            "weight on the left leg"
                        ),
                    )
                    gr.Examples(
                        examples=[[e] for e in POSE_EXAMPLES],
                        inputs=[pose_prompt],
                        label="Suggestions",
                    )
                    pose_ref = gr.Image(
                        label="or upload a reference photo",
                        type="filepath",
                        height=150,
                    )
                    gr.Markdown(
                        "Only works on a humanoid character with a detected skeleton. "
                        "Objects (cup, vase) don't have a pose.",
                        elem_classes="e3d-warning",
                    )

                split = gr.Checkbox(value=False, label="Split into parts")
                enhance = gr.Checkbox(value=True, label="Enhance image")
                license = gr.Radio(
                    choices=list(_LICENSES), value="Private", label="Usage license"
                )

                with gr.Accordion("Export as", open=True):
                    format_groups: list[gr.CheckboxGroup] = []
                    for group, formats in formats_by_group().items():
                        format_groups.append(
                            gr.CheckboxGroup(
                                choices=[(_format_label(f.ext), f.ext) for f in formats],
                                value=["glb"] if group.startswith("Web") else [],
                                label=group,
                                elem_classes="e3d-format-group",
                            )
                        )

                if not has_blender:
                    gr.Markdown(
                        "Blender not found: formats marked "
                        "*requires Blender* (.fbx, .usdz, .dae, .blend, .vrm) "
                        "can't be exported until you install it.",
                        elem_classes="e3d-warning",
                    )

                warnings = gr.Markdown("", elem_classes="e3d-warning")
                button = gr.Button("▶ Generate 3D model", variant="primary")

            with gr.Column(scale=2, min_width=380):
                preview = gr.Model3D(label="Preview", height=460)
                stats = gr.Markdown("")
                files = gr.File(label="Generated files", file_count="multiple")

    with gr.Tab("Batch (up to 10)") as batch_tab:
        gr.Markdown(
            f"The {MAX_BATCH_IMAGES} images use **the same settings as the "
            "Image → 3D tab**. To change something, go back there."
        )
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                batch_images = gr.File(
                    label=f"Images (up to {MAX_BATCH_IMAGES})",
                    file_count="multiple",
                    file_types=["image"],
                )
                batch_summary = gr.HTML(elem_classes="e3d-inherited")
                batch_button = gr.Button("▶ Generate batch", variant="primary")
            with gr.Column(scale=2, min_width=380):
                batch_progress = gr.Markdown("")
                batch_files = gr.File(
                    label="Generated files", file_count="multiple"
                )

    controls = [
        engine, topology, poly, texture, resolution, pose, pose_prompt,
        pose_ref, split, enhance, license, *format_groups,
    ]

    def _build_config(*values) -> PipelineConfig:
        (v_engine, v_topology, v_poly, v_tex, v_res, v_pose, v_prompt,
         v_ref, v_split, v_enhance, v_license, *v_formats) = values
        formats: list[str] = []
        for group in v_formats:
            formats += list(group or [])
        return PipelineConfig(
            engine=v_engine,
            topology=_TOPOLOGIES[v_topology],
            poly_count_target=int(v_poly),
            generate_texture=bool(v_tex),
            texture_resolution=_RESOLUTIONS[v_res],
            pose=_POSES[v_pose],
            pose_prompt=v_prompt or "",
            pose_ref_image=v_ref,
            split_parts=bool(v_split),
            enhance_image=bool(v_enhance),
            license=_LICENSES[v_license],
            formats=formats,
        )

    def _sync(*values):
        cfg = _build_config(*values)
        text = "\n\n".join(f"⚠️ {a}" for a in cfg.warnings())
        return cfg.to_dict(), text, _summary_table(cfg), gr.update(
            visible=cfg.pose is Pose.CUSTOM
        )

    sync_outputs = [state, warnings, batch_summary, pose_panel]
    for control in controls:
        control.change(_sync, controls, sync_outputs)

    def _generate_one(image_pil, cfg_dict, progress=gr.Progress()):
        if image_pil is None:
            raise gr.Error("Choose an image first.")
        cfg = PipelineConfig.from_dict(cfg_dict)
        result = generate(image_pil, cfg, name="model", progress=progress)
        return (
            str(result.preview) if result.preview else None,
            _stats_table(result),
            [str(a) for a in result.files],
        )

    button.click(_generate_one, [image, state], [preview, stats, files])

    def _generate_batch(paths, cfg_dict, progress=gr.Progress()):
        if not paths:
            raise gr.Error("Choose at least one image.")
        if len(paths) > MAX_BATCH_IMAGES:
            raise gr.Error(f"Maximum of {MAX_BATCH_IMAGES} images per batch.")

        from PIL import Image

        cfg = PipelineConfig.from_dict(cfg_dict)
        images = [Image.open(c).convert("RGB") for c in paths]
        names = [Path(c).stem for c in paths]
        results = generate_batch(images, cfg, names=names, progress=progress)

        all_files = [str(a) for r in results for a in r.files]
        lines = [
            f"- **{n}** — {len(r.files)} file(s), {r.duration_s}s"
            for n, r in zip(names, results)
        ]
        return "\n".join(lines), all_files

    batch_button.click(
        _generate_batch, [batch_images, state], [batch_progress, batch_files]
    )

    batch_tab.select(lambda cfg: _summary_table(PipelineConfig.from_dict(cfg)),
                    [state], [batch_summary])

    return {"preview": preview, "state": state}


def _summary_table(cfg: PipelineConfig) -> str:
    lines = {
        "Engine": ENGINES[cfg.engine].info.name if cfg.engine in ENGINES else cfg.engine,
        "Topology": cfg.topology.value.replace("_", " "),
        "Polygons": f"{cfg.poly_count_target:,}",
        "Texture": (
            f"Yes · {cfg.texture_resolution.pixels}px" if cfg.generate_texture else "No"
        ),
        "Pose": cfg.pose.value.replace("_", "-"),
        "Split into parts": "Yes" if cfg.split_parts else "No",
        "Enhance image": "Yes" if cfg.enhance_image else "No",
        "License": cfg.license.value,
        "Formats": ", ".join(f".{f}" for f in cfg.formats) or "—",
    }
    body = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in lines.items())
    return f"<b>Applied settings</b><table>{body}</table>"


def _stats_table(result) -> str:
    st = result.stats
    parts = [
        f"**Faces** {st.get('faces', 0):,}",
        f"**Parts** {result.parts}",
        f"**Time** {result.duration_s}s",
        f"**Folder** `{result.folder}`",
    ]
    text = " · ".join(parts)
    if result.warnings:
        text += "\n\n" + "\n\n".join(f"⚠️ {a}" for a in result.warnings)
    return text
