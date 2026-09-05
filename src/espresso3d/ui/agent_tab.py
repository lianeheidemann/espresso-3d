""""Agent" tab: describe what you want, confirm, generate.

The agent never triggers generation on its own. It builds the
configuration, shows the confirmation card, and only runs after
"Approve" — this avoids burning minutes of GPU time on a wrong
interpretation.
"""

from __future__ import annotations

import gradio as gr

from ..agent import backends, parser
from ..config import PipelineConfig
from ..hardware import ollama_models
from ..pipeline import generate


def _brain_options() -> list[tuple[str, str]]:
    installed = ollama_models() or []
    base_names = {m.split(":")[0] for m in installed}
    options = []
    for brain in backends.BRAINS.values():
        info = brain.info
        if info.id == "keywords":
            label = f"{info.name} — no download"
        elif info.local:
            mark = (
                "installed" if info.id.split(":")[0] in base_names
                else f"download · {info.size}"
            )
            vision = " · sees images" if info.vision else ""
            label = f"{info.name} ({mark}{vision})"
        else:
            label = f"{info.name} — needs an API key"
        options.append((label, info.id))
    return options


def build():
    with gr.Tab("Agent"):
        pending = gr.State(None)

        with gr.Row():
            with gr.Column(scale=1, min_width=340):
                brain = gr.Dropdown(
                    choices=_brain_options(),
                    value=backends.default().info.id,
                    label="Brain",
                )
                brain_info = gr.Markdown()
                on_cpu = gr.Checkbox(
                    value=True,
                    label="Run on CPU (leaves VRAM free for the 3D generator)",
                )
                conversation = gr.Chatbot(label="Conversation", height=300)
                image = gr.Image(label="Image", type="pil", height=170)
                request = gr.Textbox(
                    label="What do you want to generate?",
                    placeholder="e.g.: generate this cup separated from the saucer, high quality, in fbx",
                    lines=2,
                )
                send = gr.Button("Send", variant="primary")

                with gr.Group(visible=False) as card:
                    gr.Markdown("### Confirm generation")
                    summary = gr.HTML(elem_classes="e3d-inherited")
                    with gr.Row():
                        deny = gr.Button("Deny")
                        approve = gr.Button("Approve", variant="primary")

            with gr.Column(scale=2, min_width=380):
                stage = gr.Model3D(label="Result", height=460)
                output = gr.Markdown("Describe your idea in the chat. "
                                    "Your 3D creation will show up here.")
                files = gr.File(label="Generated files", file_count="multiple")

    def _describe(brain_id: str) -> str:
        info = backends.get(brain_id).info
        available = backends.get(brain_id).available()
        parts = [info.size, info.fits]
        if info.vision:
            parts.append("sees images")
        text = " · ".join(parts)
        if not available and info.install:
            text += f"\n\nTo use it: `{info.install}`"
        return text

    brain.change(_describe, [brain], [brain_info])

    def _interpret(text, brain_id, history):
        history = list(history or [])
        if not text.strip():
            raise gr.Error("Write what you want to generate.")

        history.append({"role": "user", "content": text})

        if brain_id == "keywords":
            cfg = parser.by_keywords(text)
            note = "Basic mode (no LLM): interpreted by keywords."
        else:
            cfg = parser.do_llm(text, backends.get(brain_id))
            note = "Here's what I understood — check it before approving:"

        history.append({"role": "assistant", "content": note})
        return history, cfg.to_dict(), gr.update(visible=True), _card(cfg), ""

    send.click(
        _interpret,
        [request, brain, conversation],
        [conversation, pending, card, summary, request],
    )

    def _deny(history):
        history = list(history or [])
        history.append({"role": "assistant", "content": "Ok, I didn't generate anything."})
        return history, gr.update(visible=False), None

    deny.click(_deny, [conversation], [conversation, card, pending])

    def _approve(image_pil, cfg_dict, history, progress=gr.Progress()):
        if image_pil is None:
            raise gr.Error("Upload the image that should become 3D.")
        if not cfg_dict:
            raise gr.Error("Nothing to generate — describe the request first.")

        cfg = PipelineConfig.from_dict(cfg_dict)
        result = generate(image_pil, cfg, name="agent", progress=progress)

        history = list(history or [])
        history.append(
            {
                "role": "assistant",
                "content": (
                    f"Done — {result.parts} object(s), "
                    f"{len(result.files)} file(s), {result.duration_s}s."
                ),
            }
        )
        details = f"Saved to `{result.folder}`"
        if result.warnings:
            details += "\n\n" + "\n\n".join(f"⚠️ {a}" for a in result.warnings)

        return (
            history,
            gr.update(visible=False),
            str(result.preview) if result.preview else None,
            details,
            [str(a) for a in result.files],
        )

    approve.click(
        _approve,
        [image, pending, conversation],
        [conversation, card, stage, output, files],
    )

    return {"stage": stage}


def _card(cfg: PipelineConfig) -> str:
    lines = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in parser.summary(cfg).items()
    )
    warnings = "".join(f"<p>⚠️ {a}</p>" for a in cfg.warnings())
    return f"<table>{lines}</table>{warnings}"
