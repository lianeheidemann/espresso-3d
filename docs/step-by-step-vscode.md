# Guia prático: levar o Espresso3D do GitHub ao VS Code

Este roteiro parte do estado atual do repositório: o código foi escrito, mas ainda não foi instalado nem executado em um computador. O objetivo é descobrir, em etapas pequenas, o que já funciona e o que precisa de correção.

> **Importante:** o repositório já contém a interface, o pipeline, três adaptadores de motores 3D, exportação e testes. Não comece reescrevendo tudo. Primeiro execute a aplicação sem motor; depois valide um motor de cada vez.

## Seu computador e o primeiro motor

A configuração registrada para seu notebook é Windows 11, NVIDIA GeForce RTX 3060 Laptop com 6 GB de VRAM e 16 GB de RAM. Para a primeira tentativa, escolha **TripoSR**: o projeto o indica para GPUs a partir de 4 GB. O Stable Fast 3D declara 6 GB como mínimo, então pode ficar sem margem de memória. O InstantMesh pede 8 GB ou mais.

A geração real exige PyTorch com CUDA e os pesos do motor. A interface pode abrir antes disso, mas abrir a interface não prova que a geração funciona.

## 1. Preparar o computador

Instale:

1. [Git for Windows](https://git-scm.com/download/win).
2. [Visual Studio Code](https://code.visualstudio.com/).
3. No VS Code, as extensões **Python** e **Pylance**, publicadas pela Microsoft.
4. Python 3.11 de 64 bits. O projeto declara Python 3.10 ou superior; 3.11 é um ponto de partida conservador para dependências de visão computacional.

Abra o PowerShell e confirme as instalações:

```powershell
git --version
py --list
nvidia-smi
```

Se o repositório continuar privado, entre no GitHub pelo navegador e autorize o Git Credential Manager quando o Git solicitar. Não coloque senha ou token dentro do endereço do clone.

## 2. Baixar o repositório e abrir no VS Code

No PowerShell, vá para a pasta onde guarda projetos e execute:

```powershell
git clone https://github.com/lianeheidemann/espresso-3d.git
cd espresso-3d
code .
```

Se `code .` não for reconhecido, abra o VS Code pelo menu Iniciar e use **File > Open Folder...** para selecionar a pasta `espresso-3d`.

Antes de alterar arquivos, crie uma branch para o trabalho:

```powershell
git switch -c test/primeira-execucao
```

No VS Code, confira a árvore do projeto. O código Python está em `src/espresso3d/`; os testes estão em `tests/`; as instruções existentes estão em `docs/software/SETUP.md`.

## 3. Criar um ambiente isolado

No terminal integrado do VS Code (**Terminal > New Terminal**), confirme que o terminal é PowerShell e rode:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
```

O terminal deve mostrar `.venv` no início da linha e Python 3.11.x. Se o PowerShell bloquear a ativação, libere-a apenas para esta janela:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

No VS Code, pressione **Ctrl+Shift+P**, escolha **Python: Select Interpreter** e selecione o Python dentro de `espresso-3d\.venv`. Isso evita instalar pacotes em outro Python do computador.

## 4. Instalar o projeto e abrir apenas a interface

Com o ambiente ativo:

```powershell
python -m pip install -e ".[dev]"
python -m espresso3d
```

A instalação editável registra o pacote que mora em `src/`. O servidor deve informar o endereço local `http://localhost:7860`; abra esse endereço no navegador.

Nesta primeira etapa, confira somente se:

- a interface abre sem traceback no terminal;
- as abas são renderizadas;
- o cabeçalho informa GPU, Blender e Ollama;
- você consegue parar o servidor com **Ctrl+C**.

Sem PyTorch com CUDA e sem um motor instalado, ainda é esperado que a criação 3D não funcione. Não instale Blender, Ollama, SAM, UniRig ou ESRGAN ainda; eles são opcionais para o primeiro modelo.

## 5. Rodar a verificação automatizada existente

O repositório já tem testes para configuração, registro de motores, exportação, redução de polígonos, biblioteca, parser do agente e validação de pose. Execute-os antes de começar a mudar o código:

```powershell
python -m pytest -q
```

Se algum teste falhar, copie o primeiro traceback completo e registre:

- comando executado;
- versão do Python (`python --version`);
- versão do pacote que falhou;
- se o ambiente `.venv` estava ativo.

Corrija uma falha por vez e rode o comando novamente. Não apague testes para fazer a execução ficar verde.

## 6. Habilitar a RTX 3060 no PyTorch

Primeiro confira se o driver NVIDIA está funcionando:

```powershell
nvidia-smi
```

Em seguida, abra o [seletor oficial de instalação do PyTorch](https://pytorch.org/get-started/locally/) e escolha **Windows**, **Pip**, **Python** e uma opção **CUDA**. Copie para o terminal o comando gerado pelo seletor. O guia antigo do repositório mostra um comando CUDA 12.4; confira o seletor atual antes de usar esse comando.

Valide a instalação:

```powershell
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA disponível:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'não detectada')"
```

Para prosseguir com geração acelerada, o resultado precisa indicar `CUDA disponível: True` e identificar a RTX 3060. Se aparecer `False`, pare aqui: confira se o terminal está usando o interpretador de `.venv` e reinstale PyTorch pelo seletor oficial. O comando `nvidia-smi` funcionar, sozinho, não prova que o PyTorch instalado consegue usar CUDA.

## 7. Instalar e testar um único motor

Comece pelo **TripoSR**. Com `.venv` ativo, use a instalação indicada no README:

```powershell
python -m pip install git+https://github.com/VAST-AI-Research/TripoSR.git
```

Feche e reabra o app no mesmo terminal. Na aba **Image → 3D**, escolha **TripoSR** explicitamente, carregue uma imagem simples de um objeto com fundo limpo e mantenha as opções básicas:

- uma imagem por vez;
- textura ligada;
- divisão em partes desligada;
- pose desligada;
- exportação `.glb`.

Clique em **Generate 3D model**. Na primeira execução, o motor pode baixar vários gigabytes de pesos; aguarde e confira o terminal. Quando concluir, verifique se o arquivo aparece na interface e foi criado em `outputs/`. Abra o GLB no visualizador e importe-o no Blender ou em outro visualizador 3D para confirmar escala, geometria e textura.

Se a VRAM acabar, tente uma imagem menor e mantenha somente uma geração ativa. Registre o erro exato antes de alterar opções ou dependências.

## 8. O que implementar depois que a primeira geração funcionar

Implemente e valide em ordem, mantendo cada mudança pequena:

1. **Inicialização reproduzível:** registrar versões de Python, PyTorch, CUDA reportada pelo PyTorch, driver e dependências do motor. Documentar um comando de instalação que funcione em uma instalação limpa.
2. **Fluxo mínimo de ponta a ponta:** imagem de entrada → um motor → malha válida → redução para a contagem de polígonos → exportação GLB → preview e registro em `outputs/`.
3. **Erros recuperáveis:** tratar falta de CUDA, falta dos pesos, falha de download, imagem inválida e falta de VRAM com mensagens claras; garantir que uma falha não deixe a interface travada.
4. **Compatibilidade dos motores:** testar TripoSR primeiro. Depois testar Stable Fast 3D separadamente; os pesos exigem aceitar a licença no Hugging Face. Só tente InstantMesh depois, pois ele pede mais VRAM.
5. **Formatos adicionais:** validar GLB, OBJ, STL e 3MF antes de instalar Blender e testar FBX, USDZ ou outros formatos que dependem dele.
6. **Opcionais:** acrescentar SAM, Real-ESRGAN, Ollama e UniRig apenas quando o fluxo básico estiver estável e houver necessidade real deles.

Há pelo menos um recurso que o próprio código marca como incompleto: a função de pose a partir de uma foto em `src/espresso3d/pipeline/rigging.py` termina com uma mensagem de “não implementado ainda”. Trate pose por foto como trabalho futuro; ela não deve bloquear o primeiro GLB. O restante das opções também precisa de validação no computador, porque os testes automatizados não substituem uma execução real do motor e da GPU.

## 9. Registrar o que foi confirmado

Depois de cada etapa, anote o resultado no README ou na documentação: sistema operacional, hardware, versões usadas, comandos que funcionaram, engine testado, formato exportado e limitações observadas. Não publique chaves de API, tokens do Hugging Face, pesos de modelos ou arquivos pessoais.

Use o Git para revisar e registrar somente as mudanças feitas:

```powershell
git status
git diff
git add docs README.md
git commit -m "docs: add VS Code first-run guide"
git push -u origin test/primeira-execucao
```

Depois, abra um Pull Request no GitHub para revisar as instruções antes de incorporá-las à branch principal.

## Critério de “primeira versão funcionando”

Considere o primeiro marco concluído quando, em uma instalação nova do projeto:

- a interface abre no VS Code/Windows;
- PyTorch identifica a RTX 3060 com CUDA disponível;
- TripoSR gera uma malha a partir de uma imagem;
- a aplicação exporta um `.glb` que abre em outro visualizador;
- a geração aparece na biblioteca em `outputs/`;
- os testes existentes terminam sem falhas.

### Referências

- [README do projeto](../../README.md)
- [Setup técnico já existente](SETUP.md)
- [Instalação local do PyTorch](https://pytorch.org/get-started/locally/)
