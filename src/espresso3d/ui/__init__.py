"""Assembly of the Gradio UI."""

from __future__ import annotations

import gradio as gr

from ..config import PipelineConfig
from ..hardware import summary_text
from . import agent_tab, library_tab, manual_tab, theme


def build_app() -> gr.Blocks:
    """Assembles the four tabs on top of a shared configuration."""
    with gr.Blocks(title="Espresso3D", fill_width=True) as app:
        gr.HTML(theme.header(summary_text()))

        # A single configuration for the Image and Batch tabs — this is
        # what makes the batch tab inherit everything instead of having
        # its own form.
        state = gr.State(PipelineConfig().to_dict())

        with gr.Tabs():
            manual_tab.build(state)
            agent_tab.build()
            library_tab.build()

    return app


def run(port: int = 7860, share: bool = False) -> None:
    app = build_app()
    app.launch(
        server_port=port,
        share=share,
        css=theme.CSS,
        theme=theme.theme(),
        show_error=True,
        inbrowser=True,
    )
