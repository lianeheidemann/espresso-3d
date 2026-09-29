# Research Framework

This package contains the scientific layer of Espresso3D and is intentionally
separated from the interactive software.

| Module | Responsibility |
|---|---|
| `dataset/` | Dataset records, input images and categories |
| `ground_truth/` | Ground-truth validation, normalization and alignment |
| `experiment_runner/` | Reproducible experiment orchestration |
| `metrics/` | Geometric and image-quality metrics |
| `hardware_profiling/` | GPU, VRAM, RAM and execution profiling |
| `statistical_analysis/` | Aggregation and statistical analysis |
| `result_visualization/` | Plots, comparisons and mesh-error visualization |

The framework should be callable without the Gradio interface. Raw experiment
outputs must remain machine-readable and preserve enough metadata to reproduce
each run.
