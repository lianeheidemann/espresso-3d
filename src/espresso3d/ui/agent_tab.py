"""Aba "Agente": descreve o que quer em português, confirma, gera.

O agente nunca dispara a geração sozinho. Ele monta a configuração,
mostra o card de confirmação, e só roda depois do "Aprovar" — evita
gastar minutos de GPU numa interpretação errada.
"""

from __future__ import annotations

import gradio as gr

from ..agent import backends, parser
from ..config import PipelineConfig
from ..hardware import ollama_modelos
from ..pipeline import gerar


def _opcoes_cerebro() -> list[tuple[str, str]]:
    instalados = ollama_modelos() or []
    nomes_base = {m.split(":")[0] for m in instalados}
    opcoes = []
    for cerebro in backends.CEREBROS.values():
        info = cerebro.info
        if info.id == "palavras_chave":
            rotulo = f"{info.nome} — sem download"
        elif info.local:
            marca = (
                "instalado" if info.id.split(":")[0] in nomes_base
                else f"baixar · {info.tamanho}"
            )
            visao = " · enxerga imagens" if info.visao else ""
            rotulo = f"{info.nome} ({marca}{visao})"
        else:
            rotulo = f"{info.nome} — precisa de chave de API"
        opcoes.append((rotulo, info.id))
    return opcoes


def construir():
    with gr.Tab("Agente"):
        pendente = gr.State(None)

        with gr.Row():
            with gr.Column(scale=1, min_width=340):
                cerebro = gr.Dropdown(
                    choices=_opcoes_cerebro(),
                    value=backends.padrao().info.id,
                    label="Cérebro",
                )
                info_cerebro = gr.Markdown()
                na_cpu = gr.Checkbox(
                    value=True,
                    label="Rodar na CPU (deixa a VRAM livre para o gerador 3D)",
                )
                conversa = gr.Chatbot(label="Conversa", height=300)
                imagem = gr.Image(label="Imagem", type="pil", height=170)
                pedido = gr.Textbox(
                    label="O que você quer gerar?",
                    placeholder="ex: gera essa xícara separada do pires, alta qualidade, em fbx",
                    lines=2,
                )
                enviar = gr.Button("Enviar", variant="primary")

                with gr.Group(visible=False) as card:
                    gr.Markdown("### Confirmar geração")
                    resumo = gr.HTML(elem_classes="e3d-herdado")
                    with gr.Row():
                        negar = gr.Button("Negar")
                        aprovar = gr.Button("Aprovar", variant="primary")

            with gr.Column(scale=2, min_width=380):
                palco = gr.Model3D(label="Resultado", height=460)
                saida = gr.Markdown("Descreva sua ideia no chat. "
                                    "Sua criação em 3D aparecerá aqui.")
                arquivos = gr.File(label="Arquivos gerados", file_count="multiple")

    def _descrever(id_cerebro: str) -> str:
        info = backends.obter(id_cerebro).info
        disponivel = backends.obter(id_cerebro).disponivel()
        partes = [info.tamanho, info.onde_cabe]
        if info.visao:
            partes.append("enxerga imagens")
        texto = " · ".join(partes)
        if not disponivel and info.instalar:
            texto += f"\n\nPara usar: `{info.instalar}`"
        return texto

    cerebro.change(_descrever, [cerebro], [info_cerebro])

    def _interpretar(texto, id_cerebro, historico):
        historico = list(historico or [])
        if not texto.strip():
            raise gr.Error("Escreva o que você quer gerar.")

        historico.append({"role": "user", "content": texto})
        motor = backends.obter(id_cerebro)

        if id_cerebro == "palavras_chave":
            cfg = parser.por_palavras_chave(texto)
            nota = "Modo básico (sem LLM): interpretei por palavras-chave."
        else:
            cfg = parser.do_llm(texto, motor)
            nota = "Entendi assim — confira antes de aprovar:"

        historico.append({"role": "assistant", "content": nota})
        return historico, cfg.como_dict(), gr.update(visible=True), _card(cfg), ""

    enviar.click(
        _interpretar,
        [pedido, cerebro, conversa],
        [conversa, pendente, card, resumo, pedido],
    )

    def _negar(historico):
        historico = list(historico or [])
        historico.append({"role": "assistant", "content": "Ok, não gerei nada."})
        return historico, gr.update(visible=False), None

    negar.click(_negar, [conversa], [conversa, card, pendente])

    def _aprovar(imagem_pil, cfg_dict, historico, progresso=gr.Progress()):
        if imagem_pil is None:
            raise gr.Error("Envie a imagem que deve virar 3D.")
        if not cfg_dict:
            raise gr.Error("Nada para gerar — descreva o pedido primeiro.")

        cfg = PipelineConfig.de_dict(cfg_dict)
        resultado = gerar(imagem_pil, cfg, nome="agente", progresso=progresso)

        historico = list(historico or [])
        historico.append(
            {
                "role": "assistant",
                "content": (
                    f"Pronto — {resultado.partes} objeto(s), "
                    f"{len(resultado.arquivos)} arquivo(s), {resultado.duracao_s}s."
                ),
            }
        )
        detalhes = f"Salvo em `{resultado.pasta}`"
        if resultado.avisos:
            detalhes += "\n\n" + "\n\n".join(f"⚠️ {a}" for a in resultado.avisos)

        return (
            historico,
            gr.update(visible=False),
            str(resultado.preview) if resultado.preview else None,
            detalhes,
            [str(a) for a in resultado.arquivos],
        )

    aprovar.click(
        _aprovar,
        [imagem, pendente, conversa],
        [conversa, card, palco, saida, arquivos],
    )

    return {"palco": palco}


def _card(cfg: PipelineConfig) -> str:
    linhas = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in parser.resumo(cfg).items()
    )
    avisos = "".join(f"<p>⚠️ {a}</p>" for a in cfg.avisos())
    return f"<table>{linhas}</table>{avisos}"
