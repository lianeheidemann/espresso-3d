""""My models" tab: view, open and delete what's already been generated."""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from ..library import store


def build():
    with gr.Tab("My models") as tab:
        with gr.Row():
            space = gr.Markdown()
            refresh = gr.Button("Refresh", scale=0)

        with gr.Row():
            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="Generated models", columns=4, height=340, object_fit="contain"
                )
            with gr.Column(scale=1, min_width=280):
                selection = gr.CheckboxGroup(choices=[], label="Select to delete")
                to_trash = gr.Checkbox(
                    value=True,
                    label="Send to the system trash (recoverable)",
                )
                delete_btn = gr.Button("Delete selected", elem_classes="e3d-danger")
                detail = gr.Markdown()

        viewer = gr.Model3D(label="View", height=380)

    def _load():
        items = store.list_items()
        count, total_bytes = len(items), sum(i.bytes for i in items)
        mb = total_bytes / (1024 * 1024)
        size = f"{mb/1024:.1f} GB" if mb >= 1024 else f"{mb:.1f} MB"
        header = (
            f"**{count}** model(s) · **{size}** in `outputs/`"
            if count
            else "No models yet. Generate the first one in the **Image → 3D** tab."
        )

        thumbnails = [
            (str(i.source_image), _label(i)) for i in items if i.source_image
        ]
        choices = [(_label(i), str(i.folder)) for i in items]
        return header, thumbnails, gr.update(choices=choices, value=[])

    def _delete(folders, trash):
        if not folders:
            raise gr.Error("Select at least one model.")
        removed = store.delete_many([Path(p) for p in folders], to_trash=trash)
        destination = "to the trash" if trash else "permanently"
        header, thumbnails, choices = _load()
        return (
            header,
            thumbnails,
            choices,
            f"{removed} model(s) deleted {destination}.",
        )

    def _open(selected_items):
        if not selected_items:
            return None, ""
        folder = Path(selected_items[0])
        glbs = sorted(folder.glob("*.glb"))
        if not glbs:
            return None, f"`{folder.name}` has no .glb to view."
        return str(glbs[0]), f"Showing `{glbs[0].name}` from `{folder}`"

    tab.select(_load, None, [space, gallery, selection])
    refresh.click(_load, None, [space, gallery, selection])
    selection.change(_open, [selection], [viewer, detail])
    delete_btn.click(_delete, [selection, to_trash], [space, gallery, selection, detail])

    return {"gallery": gallery}


def _label(item: store.Item) -> str:
    formats = " ".join(f".{f}" for f in item.formats) or "no file"
    parts = f" · {item.parts} parts" if item.parts > 1 else ""
    return f"{item.name} — {item.engine} · {item.mb} MB · {formats}{parts}"
