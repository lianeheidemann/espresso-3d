# Software layer

This package groups the application-facing parts of Espresso3D under a clear
`software` namespace.

| Module | Responsibility |
|---|---|
| `interface/` | Gradio user interface |
| `generation/` | Image-to-3D generation engines |
| `export/` | Export to 3D formats |
| `library/` | Generated-model library |
| `agent/` | Natural-language configuration agent |
| `pipeline/` | End-to-end application pipeline |

During the restructuring phase these modules act as stable public entry points
over the existing implementation. This avoids breaking the application while
the research framework is developed independently.
