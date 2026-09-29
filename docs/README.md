# Documentação

## Organização da documentação

A documentação deste repositório está separada por finalidade:

- `docs/software/`: documentação técnica do Espresso3D como aplicação;
- `docs/article/`: materiais relacionados à pesquisa e à elaboração do artigo científico.

Essa separação permite que a evolução do software seja documentada de forma independente da escrita acadêmica, embora ambos façam parte do mesmo projeto.

---

| Pasta | Para quê |
|---|---|
| [`software/`](software/) | Documentação do Espresso3D como software: levantamento técnico (tecnologias, modelos de geração 3D e agente), benchmark de reconstrução 3D e decisões em aberto. Comece por [`software/SETUP.md`](software/SETUP.md) para instalar e rodar. |
| [`article/`](article/) | Organização da escrita do artigo científico (IV 2027): documentos de trabalho, conferência alvo, divisão das seções e próximos passos. |

## Estrutura

```
docs/
├── software/
│   ├── README.md            # levantamento técnico, benchmark e decisões em aberto
│   ├── SETUP.md             # instalação e configuração do ambiente
│   ├── notas/               # explicação ilustrada das métricas LPIPS, SSIM e PSNR
│   └── images-do-readme/    # imagens usadas no README de software (exemplo do gato)
└── article/
    ├── README.md            # organização da escrita do artigo
    ├── nosso-artigo/        # documentos da equipe, numerados (proposta, rascunhos...)
    ├── references/          # referências de terceiros, numeradas
    └── notes/               # imagens de apoio (prints e figuras), com README
```

| Pasta | Conteúdo |
|---|---|
| [`software/notas/`](software/notas/) | Explicação ilustrada das métricas de comparação de imagens do benchmark (LPIPS, SSIM e PSNR). |
| [`software/images-do-readme/`](software/images-do-readme/) | Imagens exibidas no [README de software](software/README.md): fluxo de reconstrução e tabelas de resultados do exemplo do gato. |
| [`article/nosso-artigo/`](article/nosso-artigo/) | Tudo o que a equipe produz para o artigo (propostas, rascunhos, figuras, versões submetidas). |
| [`article/references/`](article/references/) | Material de terceiros usado como base de pesquisa. |
| [`article/notes/`](article/notes/) | Prints e figuras usados como apoio na escrita do artigo. |
