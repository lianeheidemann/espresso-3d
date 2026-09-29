# Artigo científico — organização da escrita

Espaço da equipe para organizar a parte escrita do artigo que está sendo
construído a partir do Espresso3D.

| | |
|---|---|
| **Título provisório** | *How Much 3D Can One Image Reveal? A Quantitative Benchmark of Open-Source 3D Reconstruction Models* |
| **Autores** | Liane Heidemann, Thiago Figueiró Ribeiro |
| **Conferência alvo** | IV 2027 — International Conference Information Visualisation |
| **Status** | Em planejamento |

---

## Documentos de trabalho (Google Docs)

A escrita acontece nestes documentos. O repositório guarda só a organização
e as referências.

- [Modelos de IA para Geração - Artigo](https://docs.google.com/document/d/1poDc_deXliMhNq3C-wGayzVEpKDgyadrlTICl-ehsXA/edit?usp=drivesdk)
- [Modelos de IA para Geração 3D - Documentação](https://docs.google.com/document/d/18NzJn0rGdpOQDcMBZqf0_p-OWwCp9N7cLGt8CAy3VPs/edit?usp=drivesdk)

---

## Conferência alvo: IV 2027

- Site: <https://iv.csites.fct.unl.pt/uk/>
- Trilha provável: **IV-App — Applications of Information Visualization**
  (ver o sumário da IV 2025 em [Referências](#referências)).

Preencher assim que o call for papers de 2027 sair:

| Item | Valor |
|---|---|
| Prazo de submissão | _a definir_ |
| Notificação de aceite | _a definir_ |
| Camera-ready | _a definir_ |
| Template / formato | _a definir_ |
| Limite de páginas | _a definir_ |

---

## Como nomear os arquivos

As três pastas abaixo (`nossos-documentos/`, `references/` e `screenshots/`)
seguem o mesmo padrão, para nada se perder:

- Nome no formato `NN_descricao-curta_Titulo.ext`, sem espaços
  (ex.: `02_rascunho-v1_How_Much_3D.docx`).
- `NN` é o próximo número livre **da própria pasta**, com dois dígitos.
- Versões diferentes do mesmo arquivo (PDF e DOCX) usam o mesmo número.
- Nunca reaproveite nem renumere um número já usado.
- Ao adicionar um arquivo, adicione também uma linha na tabela da seção
  correspondente abaixo.

---

## Nossos documentos

Tudo o que a equipe produz para o artigo (propostas, rascunhos, figuras,
versões submetidas) fica em [`nossos-documentos/`](nossos-documentos/),
numerado em ordem de criação para nada se perder.

| Nº | Documento | Arquivos | Nota |
|---|---|---|---|
| 01 | *How Much 3D Can One Image Reveal?* — proposta inicial, por Thiago Figueiró Ribeiro | [PDF](nossos-documentos/01_proposta-inicial_How_Much_3D_Can_One_Image_Reveal.pdf) | Ponto de partida do artigo. Metodologia: 5 objetos ground truth, uma foto de cada, reconstrução com TripoSR, Stable Fast 3D e InstantMesh. Comparação das meshes por Hausdorff (HD), Chamfer (CD) e MSRE; novel views por LPIPS, PSNR e SSIM. |

---

## Referências

Material de terceiros usado como base de pesquisa, em
[`references/`](references/).

| Nº | Referência | Onde | Nota |
|---|---|---|---|
| 01 | Sumário dos anais da IV 2025 (29th International Conference Information Visualisation, 5–8 ago. 2025) | [PDF](references/01_sumario-anais-IV2025_Table_of_Contents.pdf) · [IEEE CSDL](https://www.computer.org/csdl/proceedings-article/iv/2025/774100z006/2bggGgAVhbq) | Lista os artigos aceitos por trilha (incluindo IV-App). Útil para ver o tipo de trabalho aceito e levantar trabalhos relacionados. DOI 10.1109/IV68685.2025.00004. |

Referências só com link (sem arquivo) também entram na tabela e recebem
número.

---

## Capturas de tela

Prints usados como apoio, em [`screenshots/`](screenshots/).

| Nº | Captura | Arquivo | Nota |
|---|---|---|---|
| 01 | Trecho do sumário dos anais da IV 2025 | [JPG](screenshots/01_sumario-anais-IV2025_IV-App.jpg) | Mostra um trabalho de 3D aceito (*Evaluation of 2.5D and 3D Perspective Scale Breaks in Bar Charts with Outliers*) e a trilha IV-App. Complementa a referência 01. |

---

## Divisão das seções

| Seção | Responsável | Status |
|---|---|---|
| Resumo (Abstract) | | Rascunho |
| Introdução | | Não iniciado |
| Trabalhos relacionados | | Não iniciado |
| Metodologia | | Não iniciado |
| Experimentos | | Não iniciado |
| Resultados | | Não iniciado |
| Discussão | | Não iniciado |
| Conclusão | | Não iniciado |

## Próximos passos

- [ ] Escolher os 5 objetos ground truth
- [ ] Adaptar o Espresso3D para rodar o benchmark (TripoSR, Stable Fast 3D, InstantMesh)
- [ ] Implementar as métricas (HD, CD, MSRE; LPIPS, PSNR, SSIM)
- [ ] Levantar trabalhos relacionados nos proceedings da IV
- [ ] Conferir prazos e template da IV 2027
