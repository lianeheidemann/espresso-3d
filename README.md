<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark-v2.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/brand/logo-light-v2.png">
    <img width="320" alt="Espresso3D" src="assets/brand/logo-light-v2.png">
  </picture>
</p>

<p align="center"><em>Turn an image into a 3D model on your own machine.</em></p>

<p align="center">
  <img width="220" src="assets/badges/badge_em-construcao-orange-v1.svg"><br>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10 or newer">
  <img src="https://img.shields.io/badge/Gradio-6.31.0-F97316?style=for-the-badge" alt="Gradio 6.31.0">
  <img src="https://img.shields.io/badge/Trimesh-4.0%2B-475569?style=for-the-badge" alt="Trimesh 4.0 or newer"><br>
  <img src="https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy 1.24 or newer">
  <img src="https://img.shields.io/badge/Pillow-10%2B-64748B?style=for-the-badge" alt="Pillow 10 or newer">
  <img src="https://img.shields.io/badge/SciPy-1.11%2B-245C87?style=for-the-badge&logo=scipy&logoColor=white" alt="SciPy 1.11 or newer">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6D4587?style=for-the-badge" alt="MIT License"></a>
</p>

Espresso3D is a local image-to-3D application with a Gradio interface. The
interface and export tools work without a generation engine; creating models
requires CUDA-enabled PyTorch, an installed engine, and its model weights.

## Preview

<p align="center">
  <img src="assets/interface/interface-v5-2.webp" alt="Espresso3D interface preview">
</p>

[Open the interactive mockup](https://lianeheidemann.github.io/espresso-3d/) ·
The mockup previews the interface; it does not generate 3D models.

<p align="center">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

## Features

- Image-to-3D configuration, batch runs, and model library.
- Mesh processing and export to formats including GLB, OBJ, STL, FBX, USDZ,
  and VRM.
- Optional natural-language agent with Ollama or cloud providers.
- Optional image enhancement and object-part segmentation.
- Rigging, pose application, and pose extraction from photos are not yet
  implemented.

## Quick start

Requires Python 3.10 or newer. To open the local interface:

```powershell
git clone https://github.com/lianeheidemann/espresso-3d.git
cd espresso-3d
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m espresso3d
```

Open `http://localhost:7860`. For a guided Windows and VS Code setup, see
[`docs/step-by-step-vscode.md`](docs/step-by-step-vscode.md). See the
[hardware requirements](docs/requisitos-hardware.md) before selecting a 3D engine.

### 3D generation

Practical generation requires CUDA-enabled PyTorch, an engine, and its weights;
an NVIDIA GPU is recommended. CPU generation may be much slower. Engine adapters
are present, but local image generation has not yet been validated for this
project.

<p align="center">
  <img src="https://img.shields.io/badge/PyTorch-optional-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch, optional for the base app">
  <img src="https://img.shields.io/badge/CUDA-required%20for%20GPU-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA for GPU generation">
  <img src="https://img.shields.io/badge/TripoSR-optional-475569?style=for-the-badge" alt="TripoSR optional engine">
  <img src="https://img.shields.io/badge/Stable%20Fast%203D-optional-334155?style=for-the-badge" alt="Stable Fast 3D optional engine">
  <img src="https://img.shields.io/badge/InstantMesh-optional-1E40AF?style=for-the-badge" alt="InstantMesh optional engine">
</p>

| Engine | Suggested VRAM | Notes |
|---|---:|---|
| TripoSR | 4 GB+ | Fast; no PBR textures |
| Stable Fast 3D | 6 GB+ | PBR textures; check its model license for commercial use |
| InstantMesh | 8 GB+ | Multi-view generation |

Install only the engine you intend to use. Engine packages and model weights
are maintained separately and may have their own requirements and licenses.

### Optional integrations

<p align="center">
  <img src="https://img.shields.io/badge/Blender-optional-F5792A?style=for-the-badge&logo=blender&logoColor=white" alt="Blender optional integration">
  <img src="https://img.shields.io/badge/Ollama-optional-374151?style=for-the-badge" alt="Ollama optional integration">
  <img src="https://img.shields.io/badge/Segment%20Anything-optional-4158D0?style=for-the-badge" alt="Segment Anything optional integration">
  <img src="https://img.shields.io/badge/Real--ESRGAN-optional-6D28D9?style=for-the-badge" alt="Real-ESRGAN optional integration">
</p>

| Integration | Purpose | Current status |
|---|---|---|
| Blender | Additional export formats, including FBX and USDZ | Required for some formats |
| Segment Anything | Split an image into separate objects | Optional; needs a model checkpoint |
| Real-ESRGAN | Image enhancement | Optional |
| Ollama or cloud provider | Natural-language agent | Optional; keyword mode is available |
| UniRig / MediaPipe | Rigging and pose tools | Not implemented; installing them alone does not enable these features |

## Development

Install the development dependencies with `python -m pip install -e ".[dev]"`.
Run the test suite with:

<img src="https://img.shields.io/badge/pytest-8%2B-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest 8 or newer">

```powershell
python -m pytest -q
```

As of 2026-11-03, the local setup passed 81 tests on Python 3.11.9 and Gradio
6.31.0. This is an environment snapshot, not a guarantee for every supported
configuration.

### Project layout

```text
espresso-3d/
├── assets/             # project images and visual media
├── docs/               # setup and project documentation
├── mockup/             # static interactive preview published to GitHub Pages
├── src/espresso3d/     # application, engines, pipeline, agent, and library
├── tests/              # automated tests
├── AGENTS.md           # contributor guidance
├── pyproject.toml      # package metadata and dependency ranges
└── requirements.txt    # dependency list and observed versions
```

To add an engine, implement the `Engine` interface under
`src/espresso3d/engines/` and register it in `ENGINES`.

## License

The application source is licensed under [MIT](LICENSE). Integrated models and
optional tools may have separate licenses; review them before commercial use.
