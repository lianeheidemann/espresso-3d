# Setup guide — Espresso3D

What to do after cloning the repository, in order, to get from "code
downloaded" to "generating 3D from an image."

---

## Order of steps

| Step | Required? | Without it |
|---|---|---|
| 1. Base (venv + dependencies) | **Yes** | Nothing runs |
| 2. PyTorch with CUDA | **Yes, to generate** | The UI opens, but no 3D generation works |
| 3. A generation engine | **Yes, to generate** | The "Generate" button errors out explaining what's missing |
| 4. Blender | Optional | Only exports `.glb .gltf .obj .ply .stl .3mf` |
| 5. Ollama (agent) | Optional | The Agent tab falls back to keyword mode |
| 6. Extras (SAM, ESRGAN, UniRig) | Optional | The corresponding features are turned off |

**To see the first 3D model come out, you need steps 1, 2 and 3.** The
rest can be left for later.

---

## 1. Base

```bash
git clone https://github.com/lianeheidemann/espresso-3d.git
cd espresso-3d

python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
pip install -e .
```

`pip install -e .` isn't optional: the code lives in `src/`, and it's
this step that registers the package so `python -m espresso3d` works.

**Verify:**

```bash
python -m espresso3d
```

Opens at `http://localhost:7860`. Look at the **status bar in the
header** — it's the app's diagnostic panel and will tell you, at each
step from here on, what it found:

```
No CUDA GPU — will run on CPU (much slower) · Blender: not found · Ollama: off
```

At this point the following already work: the full UI, mesh
decimation, export to the lightweight formats, and the library.
**It still doesn't generate 3D.**

---

## 2. PyTorch with CUDA — the step most likely to go wrong

`pip install torch` on its own installs the **CPU version** on Windows.
It imports without error, but never uses your GPU — and the app will
run absurdly slowly without saying why. Install it pointing at the CUDA
index:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

If your card is older and the driver doesn't support CUDA 12.4, switch
to `cu121`. Check your driver version with `nvidia-smi`.

**Verify (do this, don't skip it):**

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

It needs to print `True` and your card's name. If it prints `False`,
uninstall (`pip uninstall torch torchvision`) and reinstall with the
`--index-url`.

Reopen the app: the bar should now show `GPU: 6 GB VRAM` (or whatever
yours is).

---

## 3. 3D generation engine

Pick based on the VRAM the status bar showed. Install **at least one**:

### TripoSR — 4 GB+ (start here)

```bash
pip install git+https://github.com/VAST-AI-Research/TripoSR.git
```

Lightest and fastest. Fits on any of the GPUs in your range. MIT
license, commercial use allowed. Simpler texture, no PBR.

### Stable Fast 3D — 6 GB+

```bash
pip install git+https://github.com/Stability-AI/stable-fast-3d.git
```

**Note:** the weights are *gated* on Hugging Face. Before first use:

1. Accept the license at https://huggingface.co/stabilityai/stable-fast-3d
2. `pip install huggingface_hub` and then `huggingface-cli login` with a
   token from https://huggingface.co/settings/tokens

Without this the download fails with a 401 error, which looks like an
app bug but is actually a permissions issue.

### InstantMesh — 8 GB+

```bash
git clone https://github.com/TencentARC/InstantMesh
pip install -r InstantMesh/requirements.txt
```

Highest quality of the three, and the heaviest.

### About the weights

They download on their own on the **first generation**, not at install
time — the first time takes several minutes and a few GB. They're
cached (`~/.cache/huggingface`) and won't download again. None of this
goes into Git.

**Verify:** start the app, choose the installed engine, send an image
with a clean background and click Generate. If a dependency error
shows up, it tells you the exact command that's missing.

---

## 4. Blender — for `.fbx`, `.usdz` and similar

Only needed if you want to export to Unity/Unreal (`.fbx`), iPhone AR
(`.usdz`), USD (`.usdc`/`.usda`), `.dae` or `.blend`. The web and 3D
printing formats don't depend on it.

1. Download it at https://www.blender.org/download/ (free)
2. If it's not on the PATH, point to it:

```bash
set BLENDER_BIN=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe   # Windows
export BLENDER_BIN=/path/to/blender                                           # Linux / macOS
```

**Verify:** the bar now shows `Blender: found`, and the formats that
were marked "requires Blender" become usable.

For `.vrm` (VR avatar) you still need to install the VRM add-on inside
Blender.

---

## 5. Agent — Ollama

Without this the Agent tab **doesn't break**: it falls back to a
keyword parser that understands "separated", "high quality", ".fbx",
"8000 polygons". The LLM only improves the interpretation.

1. Install from https://ollama.com
2. Download a model:

```bash
ollama pull gemma3:4b      # 3.3 GB — sees images
# or
ollama pull qwen2.5:3b     # 2.0 GB — lighter, doesn't see images
```

3. Ollama needs to be **running**. On Windows it comes up as a service
   after install; on Linux, `ollama serve`.

**Verify:**

```bash
curl http://localhost:11434/api/tags
```

Should list the model. In the app's bar `Ollama: 1 model(s)` appears,
and in the "Brain" selector on the Agent tab the model shows up as
**installed**.

> **Keep "Run on CPU" enabled.** The agent only builds a small JSON
> object; putting it on the CPU leaves the whole VRAM budget for the 3D
> generator — which is where it's actually needed. With 8 GB or less,
> LLM and 3D model on the same GPU make both fail.

If Ollama is on another machine or port: `set OLLAMA_HOST=http://ip:port`.

### Download-free alternative: free cloud tier

```bash
set GROQ_API_KEY=...          # https://console.groq.com
set OPENROUTER_API_KEY=...    # https://openrouter.ai
```

These show up in the same selector. They have a daily limit and send
your request's text outside — the image never leaves the machine, but
the request does.

---

## 6. Optional extras

| Feature | Installation | What changes |
|---|---|---|
| **Split into parts** | `pip install segment-anything` + download the `vit_b` checkpoint (~360 MB) to `checkpoints/sam_vit_b.pth` | Cup and saucer come out as two objects |
| **Enhance image** | `pip install realesrgan basicsr` | AI upscale; without it, uses Lanczos resampling |
| **Pose and skeleton** | [UniRig](https://github.com/VAST-AI-Research/UniRig) | Unlocks T-Pose, A-Pose and pose from text |
| **Pose from photo** | `pip install mediapipe` | Copies the body angles from a photo |

SAM checkpoint:
https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
(rename it to `sam_vit_b.pth` and put it in `checkpoints/`).

---

## Final checklist

Run the app and check the status bar:

- [ ] `GPU: X GB VRAM` — if it says "No CUDA GPU", go back to step 2
- [ ] `Blender: found` — if you need `.fbx`/`.usdz`
- [ ] `Ollama: N model(s)` — if you want the LLM-powered agent
- [ ] **Image → 3D** tab: generate a simple image end to end
- [ ] **My models** tab: the generated model shows up in the gallery
- [ ] `pytest -q` → 79 tests passing

---

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: espresso3d` | Missing `pip install -e .` | Run it at the repository root, with the venv active |
| Extremely slow generation, GPU idle | CPU PyTorch installed | Step 2, with `--index-url` |
| `torch.cuda.is_available()` → False | Same thing, or outdated driver | Reinstall torch; check `nvidia-smi` |
| `CUDA out of memory` | Engine too heavy, or LLM using up the VRAM | Switch to TripoSR, lower the polygon count, turn off texture, and enable "Run on CPU" on the agent |
| 401 error downloading weights | Stable Fast 3D license not accepted | Step 3, accept the license and run `huggingface-cli login` |
| `Blender not found` but it's installed | Not on the PATH | Set `BLENDER_BIN` |
| Agent doesn't respond | Ollama stopped | `ollama serve` and check `curl localhost:11434/api/tags` |
| 3D model has no texture in the file | Format doesn't carry texture | `.stl` doesn't store color; use `.glb`. The app warns before exporting |
| Pose disappeared in the exported file | Format doesn't carry a skeleton | Use `.glb`, `.fbx`, `.usdz` or `.vrm` |

---

## What lives where

```
espresso-3d/
├── outputs/          # your generated models (ignored by Git)
├── checkpoints/      # manually downloaded weights, e.g. SAM (ignored)
├── .venv/            # virtual environment (ignored)
└── src/espresso3d/   # the code
```

The engines' weights live outside the project, in the Hugging Face
cache (`~/.cache/huggingface`), shared across projects.

To uninstall everything: delete the repository folder and, if you want
to reclaim the GB used by the models, the Hugging Face cache too.
