"""Aba "Meus modelos": ver, abrir e apagar o que já foi gerado."""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from ..library import store


def construir():
    with gr.Tab("Meus modelos") as aba:
        with gr.Row():
            espaco = gr.Markdown()
            atualizar = gr.Button("Atualizar", scale=0)

        with gr.Row():
            with gr.Column(scale=2):
                galeria = gr.Gallery(
                    label="Modelos gerados", columns=4, height=340, object_fit="contain"
                )
            with gr.Column(scale=1, min_width=280):
                selecao = gr.CheckboxGroup(choices=[], label="Selecionar para apagar")
                para_lixeira = gr.Checkbox(
                    value=True,
                    label="Mandar para a lixeira do sistema (recuperável)",
                )
                apagar = gr.Button("Apagar selecionados", elem_classes="e3d-perigo")
                detalhe = gr.Markdown()

        visualizador = gr.Model3D(label="Visualizar", height=380)

    def _carregar():
        itens = store.listar()
        quantidade, bytes_totais = len(itens), sum(i.bytes for i in itens)
        mb = bytes_totais / (1024 * 1024)
        tamanho = f"{mb/1024:.1f} GB" if mb >= 1024 else f"{mb:.1f} MB"
        cabecalho = (
            f"**{quantidade}** modelo(s) · **{tamanho}** em `outputs/`"
            if quantidade
            else "Nenhum modelo ainda. Gere o primeiro na aba **Imagem → 3D**."
        )

        miniaturas = [
            (str(i.imagem_origem), _rotulo(i)) for i in itens if i.imagem_origem
        ]
        escolhas = [(_rotulo(i), str(i.pasta)) for i in itens]
        return cabecalho, miniaturas, gr.update(choices=escolhas, value=[])

    def _apagar(pastas, lixeira):
        if not pastas:
            raise gr.Error("Selecione pelo menos um modelo.")
        removidos = store.apagar_varios([Path(p) for p in pastas], para_lixeira=lixeira)
        destino = "para a lixeira" if lixeira else "definitivamente"
        cabecalho, miniaturas, escolhas = _carregar()
        return (
            cabecalho,
            miniaturas,
            escolhas,
            f"{removidos} modelo(s) apagado(s) {destino}.",
        )

    def _abrir(itens_selecionados):
        if not itens_selecionados:
            return None, ""
        pasta = Path(itens_selecionados[0])
        glbs = sorted(pasta.glob("*.glb"))
        if not glbs:
            return None, f"`{pasta.name}` não tem .glb para visualizar."
        return str(glbs[0]), f"Mostrando `{glbs[0].name}` de `{pasta}`"

    aba.select(_carregar, None, [espaco, galeria, selecao])
    atualizar.click(_carregar, None, [espaco, galeria, selecao])
    selecao.change(_abrir, [selecao], [visualizador, detalhe])
    apagar.click(_apagar, [selecao, para_lixeira], [espaco, galeria, selecao, detalhe])

    return {"galeria": galeria}


def _rotulo(item: store.Item) -> str:
    formatos = " ".join(f".{f}" for f in item.formatos) or "sem arquivo"
    partes = f" · {item.partes} partes" if item.partes > 1 else ""
    return f"{item.nome} — {item.motor} · {item.mb} MB · {formatos}{partes}"
