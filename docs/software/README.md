# Documentação do software — Espresso3D

Esta pasta reúne a documentação técnica relacionada ao **Espresso3D como software**.

O objetivo é manter, em um único local, as informações necessárias para instalar, configurar, executar, testar, manter e evoluir a aplicação, separando essa documentação dos materiais relacionados à escrita do artigo científico.

## Documentos atuais

| Documento | Finalidade |
|---|---|
| [SETUP.md](SETUP.md) | Guia de instalação e configuração do ambiente para executar o Espresso3D e gerar modelos 3D localmente. |

## Levantamento técnico

Levantamento das tecnologias que compõem o Espresso3D: o que cada uma é e por que é relevante para o projeto.

| Tecnologia | O que é | Relevância para o Espresso3D |
|---|---|---|
| **PyTorch** | Biblioteca de código aberto para aprendizado de máquina em Python, mantida pela PyTorch Foundation (originalmente pela Meta AI). Oferece tensores com aceleração por GPU e diferenciação automática, e é a base da maior parte dos modelos de visão computacional e geração 3D publicados na pesquisa. | É dependência obrigatória para **qualquer** geração 3D: os motores de geração (`engines/tripo_sr.py`, `engines/stable_fast_3d.py`), a segmentação com SAM (`pipeline/segment.py`) e o aprimoramento de imagem com ESRGAN (`pipeline/enhance.py`) são todos modelos em PyTorch. Também é usado em `hardware.py` para detectar a GPU e a VRAM disponível. |
| **CUDA** | Plataforma de computação paralela e API da NVIDIA que permite executar cálculos de propósito geral na GPU. O PyTorch a utiliza por baixo para rodar as operações dos modelos na placa de vídeo. | Sem CUDA, a inferência dos modelos roda na CPU e fica muito mais lenta, tornando a geração 3D impraticável. Por isso o PyTorch precisa ser instalado na versão com CUDA (ex.: `cu124` ou `cu121`, conforme o driver), e não na versão padrão só para CPU — ver [SETUP.md](SETUP.md#2-pytorch-with-cuda--the-step-most-likely-to-go-wrong). O app verifica `torch.cuda.is_available()` para escolher entre GPU e CPU e mostra a VRAM detectada na barra de status. |

### Modelos de geração 3D

Modelos de código aberto que transformam uma imagem em malha 3D. São os três modelos comparados no benchmark do artigo. Todos exigem PyTorch com CUDA, e os pesos são baixados do Hugging Face no primeiro uso.

| Modelo | Pesos (Hugging Face) | VRAM | Licença dos pesos | Perfil no Espresso3D |
|---|---|---|---|---|
| **TripoSR** | `stabilityai/TripoSR` | 4 GB+ | MIT | Rápido (`engines/tripo_sr.py`) |
| **Stable Fast 3D** | `stabilityai/stable-fast-3d` | 6 GB+ | Stability AI Community | Equilibrado, com textura PBR (`engines/stable_fast_3d.py`) |
| **InstantMesh** | `TencentARC/InstantMesh` | 8 GB+ | Apache 2.0 | Qualidade máxima, com textura PBR (`engines/instant_mesh.py`) |

### Agente

A aba Agente recebe um pedido em linguagem natural (ex.: "modelo detalhado em GLB para AR") e o converte numa configuração de geração (`agent/parser.py`). A configuração interpretada é sempre mostrada para a pessoa confirmar antes de rodar. O "cérebro" do agente é um LLM escolhido em `agent/backends.py`:

| Opção | Onde roda | Observação |
|---|---|---|
| **Gemma 3 4B** (`gemma3:4b`) | Local, via [Ollama](https://ollama.com) | Opção padrão recomendada: 3,3 GB, roda em qualquer GPU ou na CPU e aceita imagens |
| Qwen 2.5 3B / 7B, Llama 3.1 8B, Mistral 7B, Moondream 2B | Local, via Ollama | Alternativas locais; o LLM roda na CPU para deixar a VRAM livre para a geração 3D |
| Groq (`llama-3.1-8b-instant`) e OpenRouter (`llama-3.1-8b-instruct:free`) | Nuvem (plano gratuito) | Precisam de chave de API e internet |
| Modo básico (palavras-chave) | Local | Sem LLM: usado quando nenhum modelo está disponível |

## Decisões em aberto

Pontos que a equipe ainda precisa decidir. Ao fechar um item, marque-o e registre a decisão (e o motivo) logo abaixo dele.

- [x] **Quais inputs?**
> Malhas e fotos das malhas. As recriações das malhas seram realizadas (usando os modelos de IA) serão feitas a partir de fotos de malhas iniciais já prontas que serão usadas posteriormente como parâmetro de comparação para avaliar a qualidade dos objetos 3D gerados.
- [ ] **Quantos ângulos na reconstrução?** Reconstruir só a partir de fotos no mesmo ângulo, ou também com mais de um ângulo (ex.: frente e costas)?
- [ ] **Formato do modelo: FBX ou GLB?**
- [ ] **Como comparar as malhas geradas pelos diferentes modelos?** Que tecnologia usar: comparar renderizações/fotos em diferentes perspectivas, ou analisar a superfície com IA (talvez machine learning)?
- [ ] **Métricas e visualização dos resultados.** Quais métricas de comparação serão usadas como resultados? Como exibi-las: quais gráficos ou outros tipos de comparação usar para representar visualmente os dados obtidos?
