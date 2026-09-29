# Documentação do software — Espresso3D

Esta pasta reúne a documentação técnica relacionada ao **Espresso3D como software**.

O objetivo é manter, em um único local, as informações necessárias para instalar, configurar, executar, testar, manter e evoluir a aplicação, separando essa documentação dos materiais relacionados à escrita do artigo científico.

## O que deve ficar nesta pasta

Podem ser adicionados aqui documentos sobre:

- instalação e configuração do ambiente;
- dependências e requisitos de hardware/software;
- execução local da aplicação;
- configuração de GPU e CUDA;
- integração e configuração dos modelos de geração 3D;
- arquitetura e organização do código;
- fluxos internos e componentes do sistema;
- troubleshooting e erros conhecidos;
- testes, benchmarks técnicos e validações do software;
- instruções para desenvolvimento e manutenção;
- documentação de funcionalidades específicas.

## Documentos atuais

| Documento | Finalidade |
|---|---|
| [SETUP.md](SETUP.md) | Guia de instalação e configuração do ambiente para executar o Espresso3D e gerar modelos 3D localmente. |

## Organização da documentação

A documentação deste repositório está separada por finalidade:

- `docs/software/`: documentação técnica do Espresso3D como aplicação;
- `docs/article/`: materiais relacionados à pesquisa e à elaboração do artigo científico.

Essa separação permite que a evolução do software seja documentada de forma independente da escrita acadêmica, embora ambos façam parte do mesmo projeto.

## Como adicionar novos documentos

Ao criar uma nova documentação técnica, prefira nomes curtos e descritivos, em letras maiúsculas quando representarem guias principais. Exemplos:

```text
ARCHITECTURE.md
DEVELOPMENT.md
MODELS.md
TROUBLESHOOTING.md
BENCHMARKS.md
```

Sempre que possível, adicione também o novo documento à tabela **Documentos atuais** deste README para facilitar a navegação.
