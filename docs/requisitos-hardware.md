# Requisitos de hardware

Este guia diferencia os recursos necessários para abrir o Espresso3D daqueles
necessários para gerar modelos 3D localmente. Os requisitos de geração variam
conforme o motor, o tamanho das imagens e as opções escolhidas.

## Abrir a interface e usar os recursos básicos

- Computador capaz de executar Python 3.10 ou superior.
- A instalação básica do projeto permite abrir a interface Gradio, processar
  malhas e usar os formatos de exportação que não dependem do Blender.
- GPU NVIDIA não é necessária para abrir a interface. O aplicativo detecta
  quando não há GPU CUDA disponível e pode tentar executar na CPU, com
  desempenho muito inferior.

O projeto ainda não define um mínimo validado de RAM, processador ou espaço em
disco para essa configuração básica. Reserve espaço adicional para o ambiente
Python, arquivos gerados e, se instalar um motor, seus pesos — que podem ocupar
vários gigabytes.

## Gerar modelos 3D

Para geração local prática, use uma GPU NVIDIA compatível com CUDA e instale
uma versão do PyTorch com suporte CUDA compatível com o motor escolhido. Também
são necessários o pacote do motor e os pesos do modelo. As necessidades de VRAM
indicadas pelo projeto são:

| Motor | VRAM indicada | Observações |
|---|---:|---|
| TripoSR | 4 GB ou mais | Geração rápida; não produz texturas PBR |
| Stable Fast 3D | 6 GB ou mais | Produz texturas PBR |
| InstantMesh | 8 GB ou mais | Geração multi-view |

Esses valores são referências para escolher um motor, não garantias de que ele
funcionará em toda GPU com essa quantidade de memória. A memória disponível
também depende do sistema, da resolução, do tamanho do lote e das demais opções.
Feche aplicativos que usem a GPU e processe imagens em lotes menores se houver
falta de memória.

O projeto ainda não validou a geração local com esses motores. Portanto, a
compatibilidade real depende também das versões do sistema operacional,
PyTorch, CUDA e das dependências exigidas por cada motor. A presença de uma GPU
ou de `nvidia-smi` não confirma que o PyTorch instalado consegue usá-la.

## Componentes opcionais

| Componente | Quando é necessário | Impacto de hardware |
|---|---|---|
| Blender | Exportar alguns formatos, como FBX e USDZ | Requer espaço e memória adicionais; o projeto não define um mínimo específico |
| Ollama | Usar modelos de linguagem locais no agente | O consumo de RAM/VRAM e armazenamento depende do modelo escolhido |
| Segment Anything | Separar partes de uma imagem | Requer baixar um checkpoint; o consumo depende da imagem e do modelo |
| Real-ESRGAN | Melhorar a imagem antes da geração | Pode exigir dependências e recursos adicionais; é opcional |

UniRig e MediaPipe não devem ser instalados para atender a requisitos de
hardware neste momento: rigging, aplicação de poses e extração de pose de fotos
ainda não estão implementados.

## Configuração de referência do projeto

Em 2026-11-03, a interface e a suíte de testes foram executadas em Windows,
Python 3.11.9 e uma NVIDIA GeForce RTX 3060 com 6 GB de VRAM. Os testes passaram,
mas a geração com CUDA e os motores 3D ainda não foram validados nesse ambiente.
Essa configuração é um registro de desenvolvimento, não um requisito mínimo
nem uma certificação de compatibilidade.

Para preparar o ambiente no Windows, siga o [guia passo a passo para VS Code](step-by-step-vscode.md).
