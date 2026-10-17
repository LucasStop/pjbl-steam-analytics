# PJBL Steam Analytics — instruções para agentes

Trabalho de Data Analytics (PUCPR, prof. Marina de Lara, Turma U). Dupla: Lucas Stopinski da Silva (RA 40041246) e Lucas Bruno e Silva. Idioma: português nos textos e no notebook; identificadores, commits e PRs em inglês.

## Entregas
- **RA1** (vence 21/10/2026 18:00): avaliado pela URL do repo em `master`. Notebook `Notebooks/01_inspect_prepare.ipynb` + `docs/RA1_Data_Analytics.docx`. Não alterar a lógica nem os números.
- **RA2 — Data Stream** (vence 21/10/2026 20:00): seções 8 a 12 de `Notebooks/projeto_data_analytics.ipynb`; entrega no Canvas é o PDF `docs/projeto_data_analytics_RA1_RA2.pdf`. Roteiro da apresentação (5 min): `docs/roteiro_demo_RA2.md`.

## Decisões do RA2 (não mudar sem combinar)
- Spark Structured Streaming, cenário A (dados estáticos + chegada simulada), uma janela só: **tumbling, 5 min, média de jogadores simultâneos** por janela e por jogo.
- 3 jogos de maior `Peak CCU`, 45 leituras determinísticas (`random.Random(42)`), 3 lotes via pasta monitorada (`publicacao` -> `entrada`).
- O `assert` final (streaming == batch em pandas) precisa continuar passando.

## Pendente
- RA (matrícula) do Lucas Bruno e Silva: substituir `RA a confirmar` em `tools/build_notebook.py` (linha 18, cabeçalho do notebook) e na capa de `docs/RA1_Data_Analytics.docx`. Depois regerar o PDF com `bash tools/gerar_pdf.sh`.

## Regras
- Autoria dos commits do RA2: `--author="Lucas Bruno e Silva <cucabruno06@gmail.com>"`. PR aberto por ele; o outro integrante aprova.
- Branch `feat/...` ou `fix/...`, PR para `master` com `gh pr create`. Commit e push só quando pedido. Mensagem de commit explica o porquê.
- Nunca commitar credenciais (`~/.kaggle/kaggle.json`, `.env`). Os CSVs ficam em `Dataset/`, fora do git.
- `feat/ra2-analysis` guarda trabalho de RA3+ (API, dashboard); fora do caminho das entregas.

## Rodar
Python 3.14 (3.15 não compila o pyarrow) e Java 17.
```bash
python3.14 -m venv .venv && .venv/bin/pip install -r requirements.txt
# dados: baixar games.csv de https://drive.google.com/drive/folders/1uelu5auKv6Y-qCLQOzXuqzMDGkjlKy3m?usp=sharing (Dataset/fronkongames/) para Dataset/fronkongames/games.csv
# ou: kaggle datasets download -d fronkongames/steam-games-dataset -p Dataset/fronkongames --unzip
.venv/bin/jupyter nbconvert --to notebook --execute --inplace Notebooks/projeto_data_analytics.ipynb   # ~20 s
```

## Regerar o notebook e o PDF
O notebook é gerado: `tools/build_notebook.py` junta o template da disciplina (`tools/template_projeto_data_analytics.ipynb`) com o texto e o código do grupo. Para mudar texto ou código, editar o `build_notebook.py`, nunca só o `.ipynb`.
```bash
bash tools/gerar_pdf.sh   # gera, executa (~20 s, precisa de Dataset/ e Java 17) e exporta docs/projeto_data_analytics_RA1_RA2.pdf
```
`nbconvert --to pdf` falha (falta `tcolorbox.sty` no TeX), por isso o script usa HTML + Chrome headless (`CHROME=...` para outro caminho). Conferir: 15 páginas, seções 1 a 12 em ordem, nenhuma linha de código cortada.

## docx
É XML: `unzip` -> editar `word/document.xml` -> `zip -Xr`. Não reformatar o XML.
