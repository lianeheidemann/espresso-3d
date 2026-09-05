"""Montagem da interface Gradio."""

from __future__ import annotations

import gradio as gr

from ..config import PipelineConfig
from ..hardware import texto_resumo
from . import agent_tab, library_tab, manual_tab, theme


def construir_app() -> gr.Blocks:
    """Monta as quatro abas em cima de uma configuração compartilhada."""
    with gr.Blocks(title="Espresso3D", fill_width=True) as app:
        gr.HTML(theme.cabecalho(texto_resumo()))

        # Uma configuração só para as abas Imagem e Lote — é isso que faz o
        # lote herdar tudo em vez de ter um formulário próprio.
        estado = gr.State(PipelineConfig().como_dict())

        with gr.Tabs():
            manual_tab.construir(estado)
            agent_tab.construir()
            library_tab.construir()

    return app


def rodar(porta: int = 7860, compartilhar: bool = False) -> None:
    app = construir_app()
    app.launch(
        server_port=porta,
        share=compartilhar,
        css=theme.CSS,
        theme=theme.tema(),
        show_error=True,
        inbrowser=True,
    )
