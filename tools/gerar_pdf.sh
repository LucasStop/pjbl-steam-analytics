#!/usr/bin/env bash
# Regera o notebook (build_notebook.py), executa, e exporta o PDF de entrega (HTML + Chrome).
# nbconvert --to pdf não funciona: falta tcolorbox.sty no TeX.
# Uso, na raiz do repo: bash tools/gerar_pdf.sh   (CHROME=/caminho/chrome para outro navegador)
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
TMP=$(mktemp -d)

$PY tools/build_notebook.py
(cd Notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace projeto_data_analytics.ipynb 2>&1 | tail -1)
$PY - <<'PYEOF'
import nbformat as nbf
p = 'Notebooks/projeto_data_analytics.ipynb'
nb = nbf.read(p, as_version=4)
for c in nb.cells:
    if c.cell_type == 'code':
        c.outputs = [o for o in c.outputs if not (o.output_type == 'stream' and o.name == 'stderr')]
nbf.write(nb, p)
PYEOF

.venv/bin/jupyter nbconvert --to html Notebooks/projeto_data_analytics.ipynb --output-dir "$TMP" --output projeto 2>&1 | tail -1
# sem este CSS o código é cortado na margem direita do PDF
$PY - "$TMP/projeto.html" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
css = "<style>@page{margin:14mm}.jp-Notebook{padding:0!important}pre,code,.highlight pre,.jp-RenderedText pre{white-space:pre-wrap!important;word-break:break-word!important;overflow-wrap:anywhere!important}.jp-Cell-inputWrapper,.jp-InputArea-editor{overflow:visible!important}</style></head>"
open(p, 'w', encoding='utf-8').write(s.replace('</head>', css, 1))
PYEOF
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=docs/projeto_data_analytics_RA1_RA2.pdf "file://$TMP/projeto.html" 2>&1 | grep written
pdfinfo docs/projeto_data_analytics_RA1_RA2.pdf | grep Pages
