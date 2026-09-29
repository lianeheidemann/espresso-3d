# Levantamento Técnico — Espresso3D

Levantamento das tecnologias que compõem o Espresso3D: o que cada uma é e por que é relevante para o projeto.

| Tecnologia | O que é | Relevância para o Espresso3D |
|---|---|---|
| **PyTorch** | Biblioteca de código aberto para aprendizado de máquina em Python, mantida pela PyTorch Foundation (originalmente pela Meta AI). Oferece tensores com aceleração por GPU e diferenciação automática, e é a base da maior parte dos modelos de visão computacional e geração 3D publicados na pesquisa. | É dependência obrigatória para **qualquer** geração 3D: os motores de geração (`engines/tripo_sr.py`, `engines/stable_fast_3d.py`), a segmentação com SAM (`pipeline/segment.py`) e o aprimoramento de imagem com ESRGAN (`pipeline/enhance.py`) são todos modelos em PyTorch. Também é usado em `hardware.py` para detectar a GPU e a VRAM disponível. |
| **CUDA** | Plataforma de computação paralela e API da NVIDIA que permite executar cálculos de propósito geral na GPU. O PyTorch a utiliza por baixo para rodar as operações dos modelos na placa de vídeo. | Sem CUDA, a inferência dos modelos roda na CPU e fica muito mais lenta, tornando a geração 3D impraticável. Por isso o PyTorch precisa ser instalado na versão com CUDA (ex.: `cu124` ou `cu121`, conforme o driver), e não na versão padrão só para CPU — ver [SETUP.md](SETUP.md#2-pytorch-with-cuda--the-step-most-likely-to-go-wrong). O app verifica `torch.cuda.is_available()` para escolher entre GPU e CPU e mostra a VRAM detectada na barra de status. |
