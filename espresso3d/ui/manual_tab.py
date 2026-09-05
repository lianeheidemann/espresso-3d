"""Abas "Imagem → 3D" e "Lote".

O lote não tem painel de opções: ele lê a MESMA configuração da aba de
imagem única, guardada num ``gr.State`` compartilhado. Mudou lá, mudou aqui.
"""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from ..config import (
    FORMATOS,
    MAX_IMAGENS_LOTE,
    POLY_MAX,
    POLY_MIN,
    Licenca,
    PipelineConfig,
    Pose,
    ResolucaoTextura,
    Topologia,
    formatos_por_grupo,
)
from ..engines import MOTORES
from ..hardware import blender as achar_blender
from ..pipeline import gerar, gerar_lote

_POSES = {
    "Nenhum": Pose.NENHUM,
    "T-Pose": Pose.T_POSE,
    "A-Pose": Pose.A_POSE,
    "Personalizada": Pose.CUSTOM,
}
_TOPOLOGIAS = {"Alto Detalhe": Topologia.ALTO_DETALHE, "Smart Topology": Topologia.SMART}
_LICENCAS = {"Privado": Licenca.PRIVADA, "Comercial": Licenca.COMERCIAL}
_RESOLUCOES = {"Padrão": ResolucaoTextura.PADRAO, "Ultra 2K": ResolucaoTextura.ULTRA_2K}

EXEMPLOS_POSE = [
    "sentado de pernas cruzadas",
    "acenando com a mão direita",
    "correndo",
    "braços abertos",
    "agachado",
]


def _rotulo_formato(ext: str) -> str:
    fmt = FORMATOS[ext]
    marcas = []
    if fmt.nota:
        marcas.append(fmt.nota)
    if fmt.backend == "blender":
        marcas.append("requer Blender")
    return f".{ext}" + (f"  ({' · '.join(marcas)})" if marcas else "")


def construir(estado: gr.State):
    """Monta as duas abas e devolve os componentes que outras abas usam."""
    tem_blender = achar_blender() is not None

    with gr.Tab("Imagem → 3D"):
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                motor = gr.Radio(
                    choices=[
                        (f"{m.info.nome} — {m.info.descricao} ({m.info.vram_min_gb:g}GB+)",
                         m.info.id)
                        for m in MOTORES.values()
                    ],
                    value="stable_fast_3d",
                    label="Motor de geração",
                )
                topologia = gr.Radio(
                    choices=list(_TOPOLOGIAS), value="Alto Detalhe", label="Topologia"
                )
                imagem = gr.Image(
                    label="Imagem", type="pil", height=220, sources=["upload", "clipboard"]
                )
                poly = gr.Slider(
                    POLY_MIN, POLY_MAX, value=4000, step=100,
                    label="Contagem de polígonos",
                )
                textura = gr.Checkbox(value=True, label="Textura")
                resolucao = gr.Radio(
                    choices=list(_RESOLUCOES), value="Padrão",
                    label="Resolução de textura",
                )
                pose = gr.Radio(choices=list(_POSES), value="Nenhum", label="Pose")

                with gr.Group(visible=False) as painel_pose:
                    pose_prompt = gr.Textbox(
                        label="Descreva a pose",
                        lines=3,
                        placeholder=(
                            "ex: de pé, braços cruzados na frente do peito, "
                            "peso na perna esquerda"
                        ),
                    )
                    gr.Examples(
                        examples=[[e] for e in EXEMPLOS_POSE],
                        inputs=[pose_prompt],
                        label="Sugestões",
                    )
                    pose_ref = gr.Image(
                        label="ou envie uma foto de referência",
                        type="filepath",
                        height=150,
                    )
                    gr.Markdown(
                        "Só funciona em personagem humanoide com esqueleto detectado. "
                        "Objetos (xícara, vaso) não têm pose.",
                        elem_classes="e3d-aviso",
                    )

                dividir = gr.Checkbox(value=False, label="Dividir em partes")
                melhorar = gr.Checkbox(value=True, label="Melhorar imagem")
                licenca = gr.Radio(
                    choices=list(_LICENCAS), value="Privado", label="Licença de uso"
                )

                gr.Markdown("### Exportar como")
                grupos_fmt: list[gr.CheckboxGroup] = []
                for grupo, formatos in formatos_por_grupo().items():
                    grupos_fmt.append(
                        gr.CheckboxGroup(
                            choices=[(_rotulo_formato(f.ext), f.ext) for f in formatos],
                            value=["glb"] if grupo.startswith("Web") else [],
                            label=grupo,
                            elem_classes="e3d-grupo-formato",
                        )
                    )

                if not tem_blender:
                    gr.Markdown(
                        "Blender não encontrado: os formatos marcados com "
                        "*requer Blender* (.fbx, .usdz, .dae, .blend, .vrm) "
                        "não podem ser exportados até você instalá-lo.",
                        elem_classes="e3d-aviso",
                    )

                avisos = gr.Markdown("", elem_classes="e3d-aviso")
                botao = gr.Button("▶ Gerar modelo 3D", variant="primary")

            with gr.Column(scale=2, min_width=380):
                preview = gr.Model3D(label="Pré-visualização", height=460)
                stats = gr.Markdown("")
                arquivos = gr.File(label="Arquivos gerados", file_count="multiple")

    with gr.Tab("Lote (até 10)") as aba_lote:
        gr.Markdown(
            f"As {MAX_IMAGENS_LOTE} imagens usam **as mesmas configurações da aba "
            "Imagem → 3D**. Para mudar algo, volte lá."
        )
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                imagens_lote = gr.File(
                    label=f"Imagens (até {MAX_IMAGENS_LOTE})",
                    file_count="multiple",
                    file_types=["image"],
                )
                resumo_lote = gr.HTML(elem_classes="e3d-herdado")
                botao_lote = gr.Button("▶ Gerar em lote", variant="primary")
            with gr.Column(scale=2, min_width=380):
                progresso_lote = gr.Markdown("")
                arquivos_lote = gr.File(
                    label="Arquivos gerados", file_count="multiple"
                )

    controles = [
        motor, topologia, poly, textura, resolucao, pose, pose_prompt,
        pose_ref, dividir, melhorar, licenca, *grupos_fmt,
    ]

    def _montar(*valores) -> PipelineConfig:
        (v_motor, v_topo, v_poly, v_tex, v_res, v_pose, v_prompt,
         v_ref, v_div, v_melhor, v_lic, *v_formatos) = valores
        formatos: list[str] = []
        for grupo in v_formatos:
            formatos += list(grupo or [])
        return PipelineConfig(
            engine=v_motor,
            topologia=_TOPOLOGIAS[v_topo],
            poly_count_alvo=int(v_poly),
            gerar_textura=bool(v_tex),
            resolucao_textura=_RESOLUCOES[v_res],
            pose=_POSES[v_pose],
            pose_prompt=v_prompt or "",
            pose_ref_imagem=v_ref,
            dividir_partes=bool(v_div),
            melhorar_imagem=bool(v_melhor),
            licenca=_LICENCAS[v_lic],
            formatos=formatos,
        )

    def _sincronizar(*valores):
        cfg = _montar(*valores)
        texto = "\n\n".join(f"⚠️ {a}" for a in cfg.avisos())
        return cfg.como_dict(), texto, _tabela_resumo(cfg), gr.update(
            visible=cfg.pose is Pose.CUSTOM
        )

    saidas_sync = [estado, avisos, resumo_lote, painel_pose]
    for controle in controles:
        controle.change(_sincronizar, controles, saidas_sync)

    def _gerar_um(imagem_pil, cfg_dict, progresso=gr.Progress()):
        if imagem_pil is None:
            raise gr.Error("Escolha uma imagem primeiro.")
        cfg = PipelineConfig.de_dict(cfg_dict)
        resultado = gerar(imagem_pil, cfg, nome="modelo", progresso=progresso)
        return (
            str(resultado.preview) if resultado.preview else None,
            _tabela_stats(resultado),
            [str(a) for a in resultado.arquivos],
        )

    botao.click(_gerar_um, [imagem, estado], [preview, stats, arquivos])

    def _gerar_lote(caminhos, cfg_dict, progresso=gr.Progress()):
        if not caminhos:
            raise gr.Error("Escolha pelo menos uma imagem.")
        if len(caminhos) > MAX_IMAGENS_LOTE:
            raise gr.Error(f"Máximo de {MAX_IMAGENS_LOTE} imagens por lote.")

        from PIL import Image

        cfg = PipelineConfig.de_dict(cfg_dict)
        imagens = [Image.open(c).convert("RGB") for c in caminhos]
        nomes = [Path(c).stem for c in caminhos]
        resultados = gerar_lote(imagens, cfg, nomes=nomes, progresso=progresso)

        arquivos_todos = [str(a) for r in resultados for a in r.arquivos]
        linhas = [
            f"- **{n}** — {len(r.arquivos)} arquivo(s), {r.duracao_s}s"
            for n, r in zip(nomes, resultados)
        ]
        return "\n".join(linhas), arquivos_todos

    botao_lote.click(
        _gerar_lote, [imagens_lote, estado], [progresso_lote, arquivos_lote]
    )

    aba_lote.select(lambda cfg: _tabela_resumo(PipelineConfig.de_dict(cfg)),
                    [estado], [resumo_lote])

    return {"preview": preview, "estado": estado}


def _tabela_resumo(cfg: PipelineConfig) -> str:
    linhas = {
        "Motor": MOTORES[cfg.engine].info.nome if cfg.engine in MOTORES else cfg.engine,
        "Topologia": cfg.topologia.value.replace("_", " "),
        "Polígonos": f"{cfg.poly_count_alvo:,}".replace(",", "."),
        "Textura": (
            f"Sim · {cfg.resolucao_textura.pixels}px" if cfg.gerar_textura else "Não"
        ),
        "Pose": cfg.pose.value.replace("_", "-"),
        "Dividir em partes": "Sim" if cfg.dividir_partes else "Não",
        "Melhorar imagem": "Sim" if cfg.melhorar_imagem else "Não",
        "Licença": cfg.licenca.value,
        "Formatos": ", ".join(f".{f}" for f in cfg.formatos) or "—",
    }
    corpo = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in linhas.items())
    return f"<b>Configurações aplicadas</b><table>{corpo}</table>"


def _tabela_stats(resultado) -> str:
    est = resultado.estatisticas
    partes = [
        f"**Faces** {est.get('faces', 0):,}".replace(",", "."),
        f"**Partes** {resultado.partes}",
        f"**Tempo** {resultado.duracao_s}s",
        f"**Pasta** `{resultado.pasta}`",
    ]
    texto = " · ".join(partes)
    if resultado.avisos:
        texto += "\n\n" + "\n\n".join(f"⚠️ {a}" for a in resultado.avisos)
    return texto
