"""Aparência da interface — o mesmo tema escuro do mockup."""

from __future__ import annotations

import gradio as gr

BG = "#0a0c0f"
SURFACE = "#14171b"
SURFACE_2 = "#1b1f24"
BORDA = "#282d33"
TEXTO = "#e9ebee"
DIM = "#98a1ab"
ACCENT = "#ff8a4c"


def tema() -> gr.themes.Base:
    """Tema escuro com o âmbar de café como cor de ação."""
    return gr.themes.Base(
        primary_hue=gr.themes.colors.orange,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("IBM Plex Sans"), "system-ui", "sans-serif"],
        font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "monospace"],
    ).set(
        body_background_fill=BG,
        body_background_fill_dark=BG,
        body_text_color=TEXTO,
        body_text_color_dark=TEXTO,
        body_text_color_subdued=DIM,
        block_background_fill=SURFACE,
        block_background_fill_dark=SURFACE,
        block_border_color=BORDA,
        block_border_color_dark=BORDA,
        block_label_background_fill=SURFACE_2,
        block_label_text_color=DIM,
        block_title_text_color=TEXTO,
        border_color_primary=BORDA,
        border_color_primary_dark=BORDA,
        input_background_fill=SURFACE_2,
        input_background_fill_dark=SURFACE_2,
        input_border_color=BORDA,
        panel_background_fill=SURFACE,
        background_fill_secondary=SURFACE,
        background_fill_secondary_dark=SURFACE,
        button_primary_background_fill=f"linear-gradient(180deg,#ff9d5f,{ACCENT})",
        button_primary_background_fill_dark=f"linear-gradient(180deg,#ff9d5f,{ACCENT})",
        button_primary_text_color="#2a1102",
        button_secondary_background_fill=SURFACE_2,
        button_secondary_text_color=TEXTO,
        checkbox_background_color=SURFACE_2,
        checkbox_background_color_selected=ACCENT,
        checkbox_label_background_fill=SURFACE_2,
        checkbox_label_background_fill_selected=SURFACE_2,
        checkbox_label_text_color=TEXTO,
        slider_color=ACCENT,
    )


CSS = """
:root, .dark {
  --e3d-bg: #0a0c0f;
  --e3d-surface: #14171b;
  --e3d-surface-2: #1b1f24;
  --e3d-border: #282d33;
  --e3d-text: #e9ebee;
  --e3d-dim: #98a1ab;
  --e3d-accent: #ff8a4c;
  --e3d-agent: #5eead4;
}

.gradio-container {
  background: var(--e3d-bg) !important;
  color: var(--e3d-text) !important;
  max-width: 100% !important;
}

#e3d-topo {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  padding: 12px 16px; margin-bottom: 6px;
  border-bottom: 1px solid var(--e3d-border);
  background: linear-gradient(180deg, #101318, #0c0e12);
  border-radius: 12px;
}
#e3d-topo .marca {
  display: flex; align-items: center; gap: 10px;
}
#e3d-topo .simbolo {
  width: 32px; height: 32px; border-radius: 9px; flex: none;
  background: linear-gradient(135deg, #ff9d5f, #c65a24);
  display: flex; align-items: center; justify-content: center; font-size: 17px;
}
#e3d-topo h1 {
  font-size: 17px; margin: 0; font-weight: 800; letter-spacing: .2px;
  color: var(--e3d-text) !important;
}
#e3d-topo .sub { font-size: 12px; color: #7d868f; margin-top: 1px; }
#e3d-topo .status {
  margin-left: auto; font-size: 12px; color: var(--e3d-dim);
  background: var(--e3d-surface-2); border: 1px solid var(--e3d-border);
  border-radius: 999px; padding: 6px 14px;
}

.e3d-grupo-formato { border-left: 2px solid var(--e3d-border); padding-left: 10px; }

.e3d-aviso {
  background: #f2c14e14; border: 1px solid #f2c14e33; border-radius: 9px;
  padding: 10px 12px; font-size: 13px; color: #e0c690;
}
.e3d-aviso:empty { display: none; }

.e3d-herdado {
  background: var(--e3d-surface); border: 1px solid var(--e3d-border);
  border-radius: 11px; padding: 4px 14px;
}
.e3d-herdado table { width: 100%; font-size: 13px; }
.e3d-herdado td { padding: 5px 0; border-bottom: 1px solid #1e2227; }
.e3d-herdado td:last-child { text-align: right; font-family: ui-monospace, monospace; }
.e3d-herdado tr:last-child td { border-bottom: none; }

button.primary, .primary button {
  background: linear-gradient(180deg, #ff9d5f, var(--e3d-accent)) !important;
  color: #2a1102 !important; font-weight: 700 !important; border: none !important;
}
.e3d-perigo button {
  background: #e0666614 !important; color: #f0a0a0 !important;
  border: 1px solid #e0666655 !important;
}
footer { display: none !important; }
"""


def cabecalho(status: str) -> str:
    """Barra superior com a marca e o status do hardware."""
    return f"""
<div id="e3d-topo">
  <div class="marca">
    <div class="simbolo">☕</div>
    <div>
      <h1>Espresso3D</h1>
      <div class="sub">gerador local de imagem → 3D, 100% seu</div>
    </div>
  </div>
  <div class="status">{status}</div>
</div>
"""
