"""UI appearance — translated from the GitHub Pages mockup to Gradio."""

from __future__ import annotations

import gradio as gr

BG = "#0a0c0f"
SURFACE = "#14171b"
SURFACE_2 = "#1b1f24"
BORDER = "#282d33"
TEXT = "#e9ebee"
DIM = "#98a1ab"
FAINT = "#5f6870"
ACCENT = "#ff8a4c"
SURFACE_3 = "#22262c"


def theme() -> gr.themes.Base:
    """Dark theme with coffee amber as the action color."""
    return gr.themes.Base(
        primary_hue=gr.themes.colors.orange,
        neutral_hue=gr.themes.colors.slate,
        font=[
            gr.themes.GoogleFont("IBM Plex Sans"),
            "system-ui",
            "sans-serif",
        ],
        font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "monospace"],
    ).set(
        body_background_fill=BG,
        body_background_fill_dark=BG,
        body_text_color=TEXT,
        body_text_color_dark=TEXT,
        body_text_color_subdued=DIM,
        block_background_fill=SURFACE,
        block_background_fill_dark=SURFACE,
        block_border_color=BORDER,
        block_border_color_dark=BORDER,
        block_label_background_fill=SURFACE_2,
        block_label_text_color=DIM,
        block_title_text_color=TEXT,
        border_color_primary=BORDER,
        border_color_primary_dark=BORDER,
        input_background_fill=SURFACE_2,
        input_background_fill_dark=SURFACE_2,
        input_border_color=BORDER,
        panel_background_fill=SURFACE,
        background_fill_secondary=SURFACE,
        background_fill_secondary_dark=SURFACE,
        button_primary_background_fill=f"linear-gradient(180deg,#ff9d5f,{ACCENT})",
        button_primary_background_fill_dark=f"linear-gradient(180deg,#ff9d5f,{ACCENT})",
        button_primary_text_color="#2a1102",
        button_secondary_background_fill=SURFACE_2,
        button_secondary_text_color=TEXT,
        checkbox_background_color=SURFACE_2,
        checkbox_background_color_selected=ACCENT,
        checkbox_label_background_fill=SURFACE_2,
        checkbox_label_background_fill_selected=SURFACE_2,
        checkbox_label_text_color=TEXT,
        slider_color=ACCENT,
    )


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&display=swap');

:root, .dark, #e3d-app {
  color-scheme: dark;
  --e3d-bg: #0a0c0f;
  --e3d-surface: #14171b;
  --e3d-surface-2: #1b1f24;
  --e3d-surface-3: #22262c;
  --e3d-border: #282d33;
  --e3d-text: #e9ebee;
  --e3d-dim: #98a1ab;
  --e3d-faint: #5f6870;
  --e3d-accent: #ff8a4c;
  --e3d-agent: #5eead4;
}

#e3d-app, #e3d-app * {
  box-sizing: border-box;
}

#e3d-app {
  background: var(--e3d-bg) !important;
  color: var(--e3d-text) !important;
  font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}

.gradio-container:has(#e3d-app) {
  max-width: 100% !important;
  padding: 12px 18px 20px !important;
  background: var(--e3d-bg) !important;
  color: var(--e3d-text) !important;
  font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}

.gradio-container:has(#e3d-app) h1,
.gradio-container:has(#e3d-app) h2,
.gradio-container:has(#e3d-app) h3 {
  font-family: Manrope, 'IBM Plex Sans', system-ui, sans-serif !important;
}

#e3d-topbar {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  padding: 12px 20px; margin-bottom: 12px;
  border-bottom: 1px solid var(--e3d-border); border-radius: 12px;
  background: linear-gradient(180deg, #101318, #0c0e12);
}
#e3d-topbar .brand {
  display: flex; align-items: center; gap: 10px;
}
#e3d-topbar .symbol {
  width: 30px; height: 30px; border-radius: 8px; flex: none;
  background: linear-gradient(135deg, #ff9d5f, #c65a24);
  display: flex; align-items: center; justify-content: center; font-size: 16px;
  color: #241005;
}
#e3d-topbar h1 {
  font-family: Manrope, 'IBM Plex Sans', system-ui, sans-serif !important;
  font-size: 16px; margin: 0; font-weight: 800; letter-spacing: .2px;
  color: var(--e3d-text) !important;
}
#e3d-topbar .sub { font-size: 12px; color: var(--e3d-faint); margin-top: 1px; }
#e3d-topbar .status {
  margin-left: auto; font-size: 12px; color: var(--e3d-dim);
  background: var(--e3d-surface-2); border: 1px solid var(--e3d-border);
  border-radius: 999px; padding: 6px 12px;
}

/* Match the Pages mockup's compact navigation and workstation proportions. */
#e3d-tabs > .tab-nav {
  display: flex !important; align-items: center; gap: 4px;
  width: max-content; max-width: 100%; margin: 0 0 8px !important;
  padding: 4px !important; border: 1px solid var(--e3d-border) !important;
  border-radius: 12px !important; background: var(--e3d-surface) !important;
}
#e3d-tabs > .tab-nav button {
  min-height: 34px; padding: 7px 14px !important; border: 0 !important;
  border-radius: 8px !important; background: transparent !important;
  color: var(--e3d-dim) !important; font-size: 13px !important;
  font-weight: 500 !important; box-shadow: none !important;
}
#e3d-tabs > .tab-nav button:hover { color: var(--e3d-text) !important; }
#e3d-tabs > .tab-nav button.selected,
#e3d-tabs > .tab-nav button[aria-selected="true"] {
  background: var(--e3d-surface-3) !important; color: var(--e3d-text) !important;
  box-shadow: inset 0 0 0 1px var(--e3d-border) !important;
}
#e3d-tabs > .tab-nav::after { display: none !important; }
#e3d-tabs > .tabitem { padding: 0 !important; }

#e3d-main-layout {
  display: grid !important;
  grid-template-columns: 312px minmax(0, 1fr) !important;
  gap: 0 !important; align-items: stretch !important;
  min-height: calc(100vh - 142px);
}
#e3d-config {
  width: 312px !important; min-width: 0 !important; max-width: none !important;
  padding: 18px 16px 10px !important; gap: 14px !important;
  overflow-y: auto; border-right: 1px solid #1e2227;
}
#e3d-stage {
  min-width: 0 !important; padding: 0 0 0 16px !important;
  background: radial-gradient(120% 90% at 50% 0%, #151a20 0%, var(--e3d-bg) 60%);
}
#e3d-config .block, #e3d-stage .block {
  background: transparent !important; border-color: transparent !important;
  box-shadow: none !important;
}
#e3d-config .block > label,
#e3d-config .block > .wrap > label,
#e3d-config fieldset > legend {
  color: var(--e3d-dim) !important; font-size: 12.5px !important;
  font-weight: 600 !important; margin-bottom: 7px !important;
}

/* Radio cards become the restrained segmented controls from the mockup. */
#e3d-config .e3d-segmented [role="radiogroup"],
#e3d-config .e3d-segmented .wrap,
#e3d-config .e3d-segmented .flex-wrap {
  display: flex !important; flex-wrap: wrap; gap: 4px !important;
  padding: 3px !important; border: 1px solid var(--e3d-border) !important;
  border-radius: 9px !important; background: var(--e3d-surface) !important;
}
#e3d-config .e3d-segmented label,
#e3d-config .e3d-engine-choice label {
  border: 1px solid var(--e3d-border) !important; border-radius: 8px !important;
  background: var(--e3d-surface) !important; color: var(--e3d-dim) !important;
  transition: background .15s ease, border-color .15s ease, color .15s ease;
}
#e3d-config .e3d-segmented label { padding: 7px 9px !important; }
#e3d-config .e3d-segmented label:has(input:checked),
#e3d-config .e3d-engine-choice label:has(input:checked) {
  border-color: var(--e3d-accent) !important;
  background: #ff8a4c26 !important; color: var(--e3d-text) !important;
}
#e3d-config .e3d-engine-choice label {
  min-height: 52px; padding: 8px 10px !important;
}
#e3d-config .e3d-engine-choice [role="radiogroup"] { gap: 6px !important; }

#e3d-image-upload {
  overflow: hidden; border: 1.5px dashed var(--e3d-border) !important;
  border-radius: 12px !important; background: var(--e3d-surface) !important;
}
#e3d-image-upload:hover { border-color: var(--e3d-faint) !important; }
#e3d-image-upload [data-testid="image"] { background: transparent !important; }
#e3d-image-upload [data-testid="image"] button { color: var(--e3d-accent) !important; }
#e3d-config input[type="range"] { accent-color: var(--e3d-accent) !important; }
#e3d-config input[type="checkbox"] { accent-color: var(--e3d-accent) !important; }
#e3d-config input:not([type="checkbox"]):not([type="radio"]),
#e3d-config textarea, #e3d-config select {
  background-color: var(--e3d-surface-2) !important;
  border-color: var(--e3d-border) !important; color: var(--e3d-text) !important;
}
#e3d-config .e3d-format-group { border-left: 2px solid var(--e3d-border); padding-left: 10px; }

#e3d-preview {
  min-height: 460px; border: 1px solid var(--e3d-border) !important;
  border-radius: 10px !important; background: var(--e3d-surface) !important;
}
#e3d-stage > * { min-width: 0; }
#e3d-config button.primary, #e3d-config .primary button,
#e3d-stage button.primary, #e3d-stage .primary button {
  background: linear-gradient(180deg, #ff9d5f, var(--e3d-accent)) !important;
  color: #241005 !important; font-weight: 700 !important; border: none !important;
}
#e3d-config button:focus-visible, #e3d-tabs button:focus-visible {
  outline: 2px solid var(--e3d-accent) !important; outline-offset: 2px !important;
}

.e3d-format-group { border-left: 2px solid var(--e3d-border); padding-left: 10px; }

.e3d-warning {
  background: #f2c14e14; border: 1px solid #f2c14e33; border-radius: 9px;
  padding: 10px 12px; font-size: 13px; color: #e0c690;
}
.e3d-warning:empty { display: none; }

.e3d-inherited {
  background: var(--e3d-surface); border: 1px solid var(--e3d-border);
  border-radius: 11px; padding: 4px 14px;
}
.e3d-inherited table { width: 100%; font-size: 13px; }
.e3d-inherited td { padding: 5px 0; border-bottom: 1px solid #1e2227; }
.e3d-inherited td:last-child { text-align: right; font-family: ui-monospace, monospace; }
.e3d-inherited tr:last-child td { border-bottom: none; }

.e3d-danger button {
  background: #e0666614 !important; color: #f0a0a0 !important;
  border: 1px solid #e0666655 !important;
}
footer { display: none !important; }

@media (max-width: 900px) {
  .gradio-container:has(#e3d-app) { padding: 8px 10px 16px !important; }
  #e3d-main-layout { grid-template-columns: minmax(0, 1fr) !important; }
  #e3d-config {
    width: 100% !important; border-right: 0; border-bottom: 1px solid #1e2227;
    overflow: visible; padding: 14px 8px !important;
  }
  #e3d-stage { padding: 12px 0 0 !important; min-height: 380px; }
  #e3d-tabs > .tab-nav { width: 100%; display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  #e3d-tabs > .tab-nav button { justify-content: center; padding-inline: 6px !important; }
}

@media (prefers-reduced-motion: reduce) {
  #e3d-app *, #e3d-app *::before, #e3d-app *::after { transition: none !important; animation: none !important; }
}
"""


def header(status: str) -> str:
    """Top bar with the brand and hardware status."""
    return f"""
<div id="e3d-topbar">
  <div class="brand">
    <div class="symbol">☕</div>
    <div>
      <h1>Espresso3D</h1>
      <div class="sub">local image → 3D generator, 100% yours</div>
    </div>
  </div>
  <div class="status">{status}</div>
</div>
"""
