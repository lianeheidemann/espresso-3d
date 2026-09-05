# Guia de instalação — Espresso3D

O que fazer depois de clonar o repositório, na ordem, para sair de "código
baixado" até "gerando 3D a partir de imagem".

Este guia está em português porque é o seu roteiro de operação. O
[README](../README.md) é a porta de entrada pública, em inglês.

---

## Ordem das etapas

| Etapa | Obrigatória? | Sem ela |
|---|---|---|
| 1. Base (venv + dependências) | **Sim** | Nada roda |
| 2. PyTorch com CUDA | **Sim para gerar** | A interface abre, mas nenhuma geração 3D funciona |
| 3. Um motor de geração | **Sim para gerar** | Botão "Gerar" dá erro explicando o que falta |
| 4. Blender | Opcional | Só exporta `.glb .gltf .obj .ply .stl .3mf` |
| 5. Ollama (agente) | Opcional | Aba Agente cai no modo palavras-chave |
| 6. Extras (SAM, ESRGAN, UniRig) | Opcional | Recursos correspondentes desligados |

**Para ver o primeiro modelo 3D sair, você precisa das etapas 1, 2 e 3.** O
resto dá para deixar para depois.

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

O `pip install -e .` não é opcional: o código vive em `src/`, e é ele que
registra o pacote para o `python -m espresso3d` funcionar.

**Verificar:**

```bash
python -m espresso3d
```

Abre em `http://localhost:7860`. Olhe a **faixa de status no cabeçalho** — ela
é o painel de diagnóstico do app e vai dizer, a cada etapa daqui pra frente,
o que ele encontrou:

```
Sem GPU CUDA — vai rodar na CPU (bem mais lento) · Blender: não encontrado · Ollama: desligado
```

Neste momento já funcionam: interface completa, redução de malha, exportação
para os formatos leves e a biblioteca. **Ainda não gera 3D.**

---

## 2. PyTorch com CUDA — a etapa que mais dá errado

`pip install torch` sozinho instala a **versão CPU** no Windows. Ela importa
sem erro, mas nunca usa a sua GPU — e o app vai rodar absurdamente lento sem
dizer o motivo. Instale apontando o índice do CUDA:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

Se sua placa for antiga e o driver não suportar CUDA 12.4, troque para
`cu121`. Confira a versão do driver com `nvidia-smi`.

**Verificar (faça isso, não pule):**

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Precisa imprimir `True` e o nome da sua placa. Se imprimir `False`,
desinstale (`pip uninstall torch torchvision`) e instale de novo com o
`--index-url`.

Reabra o app: a faixa deve passar a mostrar `GPU: 6 GB VRAM` (ou o que for a
sua).

---

## 3. Motor de geração 3D

Escolha pela VRAM que a faixa de status mostrou. Instale **pelo menos um**:

### TripoSR — 4 GB+ (comece por aqui)

```bash
pip install git+https://github.com/VAST-AI-Research/TripoSR.git
```

Mais leve e mais rápido. Cabe em qualquer uma das GPUs da sua faixa. Licença
MIT, uso comercial liberado. Textura mais simples, sem PBR.

### Stable Fast 3D — 6 GB+

```bash
pip install git+https://github.com/Stability-AI/stable-fast-3d.git
```

**Atenção:** os pesos são *gated* no Hugging Face. Antes do primeiro uso:

1. Aceite a licença em https://huggingface.co/stabilityai/stable-fast-3d
2. `pip install huggingface_hub` e depois `huggingface-cli login` com um
   token de https://huggingface.co/settings/tokens

Sem isso o download falha com erro 401, que parece bug do app mas é permissão.

### InstantMesh — 8 GB+

```bash
git clone https://github.com/TencentARC/InstantMesh
pip install -r InstantMesh/requirements.txt
```

Maior qualidade dos três, e o mais pesado.

### Sobre os pesos

Baixam sozinhos na **primeira geração**, não na instalação — a primeira vez
demora vários minutos e alguns GB. Ficam em cache (`~/.cache/huggingface`) e
não voltam a baixar. Nada disso entra no Git.

**Verificar:** suba o app, escolha o motor instalado, mande uma imagem com
fundo limpo e clique em Gerar. Se aparecer erro de dependência, ele diz o
comando exato que falta.

---

## 4. Blender — para `.fbx`, `.usdz` e afins

Só é preciso se você quiser exportar para Unity/Unreal (`.fbx`), AR do iPhone
(`.usdz`), USD (`.usdc`/`.usda`), `.dae` ou `.blend`. Os formatos de web e
impressão 3D não dependem dele.

1. Baixe em https://www.blender.org/download/ (grátis)
2. Se não estiver no PATH, aponte:

```bash
set BLENDER_BIN=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe   # Windows
export BLENDER_BIN=/caminho/para/blender                                       # Linux / macOS
```

**Verificar:** a faixa passa a mostrar `Blender: encontrado`, e os formatos
que estavam marcados com "requer Blender" ficam utilizáveis.

Para `.vrm` (avatar VR) ainda falta instalar o add-on VRM dentro do Blender.

---

## 5. Agente — Ollama

Sem isso a aba Agente **não quebra**: ela cai num interpretador por
palavras-chave que entende "separado", "alta qualidade", ".fbx", "8000
polígonos". O LLM só melhora a interpretação.

1. Instale de https://ollama.com
2. Baixe um modelo:

```bash
ollama pull gemma3:4b      # 3,3 GB — enxerga imagens
# ou
ollama pull qwen2.5:3b     # 2,0 GB — mais leve, não enxerga imagens
```

3. O Ollama precisa estar **rodando**. No Windows ele sobe como serviço depois
   da instalação; no Linux, `ollama serve`.

**Verificar:**

```bash
curl http://localhost:11434/api/tags
```

Deve listar o modelo. Na faixa do app aparece `Ollama: 1 modelo(s)`, e no
seletor "Cérebro" da aba Agente o modelo aparece como **instalado**.

> **Deixe "Rodar na CPU" ligado.** O agente só monta um JSON pequeno; jogando
> ele na CPU, a VRAM inteira sobra para o gerador 3D — que é onde ela faz
> falta. Com 8 GB ou menos, LLM e modelo 3D na mesma GPU fazem os dois falharem.

Se o Ollama estiver em outra máquina ou porta: `set OLLAMA_HOST=http://ip:porta`.

### Alternativa sem download: nuvem gratuita

```bash
set GROQ_API_KEY=...          # https://console.groq.com
set OPENROUTER_API_KEY=...    # https://openrouter.ai
```

Aparecem no mesmo seletor. Têm limite diário e mandam o texto do seu pedido
para fora — a imagem não sai da máquina, mas o pedido sim.

---

## 6. Extras opcionais

| Recurso | Instalação | O que muda |
|---|---|---|
| **Dividir em partes** | `pip install segment-anything` + baixar o checkpoint `vit_b` (~360 MB) para `checkpoints/sam_vit_b.pth` | Xícara e pires saem como dois objetos |
| **Melhorar imagem** | `pip install realesrgan basicsr` | Upscale com IA; sem isso usa reamostragem Lanczos |
| **Pose e esqueleto** | [UniRig](https://github.com/VAST-AI-Research/UniRig) | Libera T-Pose, A-Pose e pose por texto |
| **Pose por foto** | `pip install mediapipe` | Copia os ângulos do corpo de uma foto |

Checkpoint do SAM:
https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
(renomeie para `sam_vit_b.pth` e coloque em `checkpoints/`).

---

## Checklist final

Rode o app e confira a faixa de status:

- [ ] `GPU: X GB VRAM` — se disser "Sem GPU CUDA", volte à etapa 2
- [ ] `Blender: encontrado` — se precisar de `.fbx`/`.usdz`
- [ ] `Ollama: N modelo(s)` — se quiser o agente com LLM
- [ ] Aba **Imagem → 3D**: gerar uma imagem simples ponta a ponta
- [ ] Aba **Meus modelos**: o modelo gerado aparece na galeria
- [ ] `pytest -q` → 79 testes passando

---

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: espresso3d` | Faltou o `pip install -e .` | Rode na raiz do repositório, com a venv ativa |
| Geração lentíssima, GPU parada | PyTorch CPU instalado | Etapa 2, com `--index-url` |
| `torch.cuda.is_available()` → False | Mesma coisa, ou driver desatualizado | Reinstale o torch; confira `nvidia-smi` |
| `CUDA out of memory` | Motor pesado demais, ou LLM ocupando a VRAM | Troque para TripoSR, baixe a contagem de polígonos, desligue textura, e ligue "Rodar na CPU" no agente |
| Erro 401 ao baixar pesos | Licença do Stable Fast 3D não aceita | Etapa 3, aceite a licença e faça `huggingface-cli login` |
| `Blender não encontrado` mas está instalado | Fora do PATH | Defina `BLENDER_BIN` |
| Agente não responde | Ollama parado | `ollama serve` e confira `curl localhost:11434/api/tags` |
| Modelo 3D sem textura no arquivo | Formato não carrega textura | `.stl` não guarda cor; use `.glb`. O app avisa antes de exportar |
| Pose sumiu no arquivo exportado | Formato não carrega esqueleto | Use `.glb`, `.fbx`, `.usdz` ou `.vrm` |

---

## O que fica onde

```
espresso-3d/
├── outputs/          # seus modelos gerados (ignorado pelo Git)
├── checkpoints/      # pesos baixados manualmente, ex. SAM (ignorado)
├── .venv/            # ambiente virtual (ignorado)
└── src/espresso3d/   # o código
```

Os pesos dos motores ficam fora do projeto, no cache do Hugging Face
(`~/.cache/huggingface`), compartilhado entre projetos.

Para desinstalar tudo: apague a pasta do repositório e, se quiser recuperar
os GB dos modelos, o cache do Hugging Face.
