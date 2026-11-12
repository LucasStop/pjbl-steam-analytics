# PJBL — Data Analytics (Steam)

## Grupo
Lucas Stopinski da Silva, Lucas Bruno e Silva.

## Contexto e pergunta de pesquisa
Contexto: jogos, especificamente a plataforma **Steam**.

Pergunta inicial: *Quais características de um jogo na Steam (preço, gênero/tags, nota de review) estão associadas a maior pico de jogadores simultâneos, e como o catálogo histórico se compara ao comportamento ao vivo dos jogos mais jogados agora?*

**Perguntas analíticas** (guiam RA2 em diante):
1. Jogos mais caros têm pico de jogadores simultâneos (`Peak CCU`) maior ou menor? Existe faixa de preço associada aos maiores picos?
2. Quais gêneros e tags concentram os jogos com maior `Peak CCU`?
3. A nota de review (proporção `Positive` / `Negative`) se relaciona com o `Peak CCU`, e a nota do Metacritic acrescenta algo além disso?
4. O catálogo histórico (Kaggle) é consistente com o dado ao vivo (Steam Web API / SteamSpy) para os jogos mais jogados agora?

Dados necessários: catálogo com preço, gênero/tags, reviews e pico de jogadores (histórico) + jogadores/preço atual por jogo (ao vivo).

**Classificação dos dados:** majoritariamente **estruturado** — os 4 datasets do Kaggle são tabulares (CSV) e as duas APIs (Steam Web API, SteamSpy) retornam JSON estruturado por campo. Não há dado não-estruturado no projeto (não usamos texto livre de review nem imagem/vídeo).

**Tipo de analytics:** **descritivo** (perfil do catálogo — distribuição de preço, gênero, nota) e **diagnóstico** (o que diferencia jogos com pico de jogadores alto dos demais), e, a partir do RA3, **preditivo** (regressão supervisionada de `log10(Peak CCU)`, seção 16 do notebook). Não há componente prescritivo.

## Fontes de dados

| Fonte (origem) | Formato | Registros | Principais atributos | Relação com o problema |
|---|---|---|---|---|
| [fronkongames/steam-games-dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) (Kaggle) | CSV | 125.855 linhas × 40 colunas (42 após preparo) | `AppID`, `Name`, `Release date`, `Price`, `Peak CCU`, `Estimated owners`, `Positive`/`Negative`, `Metacritic score`, `Genres`, `Tags` | **Base principal**: contém todas as variáveis das perguntas 1 a 3 |
| [srgiomanhes/steam-games-dataset-2025](https://www.kaggle.com/datasets/srgiomanhes/steam-games-dataset-2025) (Kaggle) | CSV | 71.429 × 21 | `steam_appid`, `name`, `genres`, `price_initial (USD)`, `total_positive`/`total_negative`, `metacritic` | Checagem de consistência de preço e reviews da base principal |
| [waddahali/top-1000-steam-games-2024-2026](https://www.kaggle.com/datasets/waddahali/top-1000-steam-games-20242026) (Kaggle) | CSV | 1.000 × 12 | `AppID`, `Price_USD`, `Primary_Genre`, `All_Tags`, `Review_Score_Pct`, `24h_Peak_Players` | Validação cruzada de `Peak CCU` e preço (catalogada; fora das entregas) |
| [andrewmvd/steam-reviews](https://www.kaggle.com/datasets/andrewmvd/steam-reviews/versions/3) (Kaggle) | CSV (2,16 GB) | 6.417.106 | texto e voto de review por `app_id` | Catalogada; **fora das entregas** |
| [Steam Web API](https://partner.steamgames.com/doc/webapi_overview) + [SteamSpy API](https://steamspy.com/api.php) | JSON (API) | por `appid` consultado | jogadores atuais, preço atual | Pergunta 4 (dado ao vivo); **não coletado** nas entregas |

**Ingestão (RA1):** os CSVs não vão pro GitHub (limite de 100 MB/arquivo). Cópia dos dados no [Google Drive do grupo](https://drive.google.com/drive/folders/1uelu5auKv6Y-qCLQOzXuqzMDGkjlKy3m?usp=sharing): baixe a pasta `Dataset/` e coloque na raiz do projeto (os notebooks só precisam de `Dataset/fronkongames/games.csv`). Alternativa direto do Kaggle: `pip install -r requirements.txt`, configurar `~/.kaggle/kaggle.json` e rodar `kaggle datasets download -d fronkongames/steam-games-dataset -p Dataset/fronkongames --unzip`. O notebook `01_inspect_prepare.ipynb` valida a presença de `Dataset/fronkongames/games.csv` e gera `games_clean.csv`.

## Ferramentas — decisão e por quê

**Pandas no batch; Spark só no streaming do RA2.** O maior dataset (~125 mil linhas, cerca de 400 MB) processa em memória em segundos numa máquina só, então a ingestão e a limpeza (RA1) e a análise e o modelo (RA3) usam pandas e scikit-learn; Spark/Hadoop só compensam em volume GB–TB ou processamento distribuído e seriam over-engineering para essas etapas. O Spark entra apenas no RA2, em modo local, porque o enunciado pede Spark Structured Streaming para demonstrar o processamento em fluxo e as janelas temporais.

**Streamlit, não Power BI (dashboard fora das entregas).** Decisão original era Power BI, revertida ao descobrir que **Power BI Desktop não roda nativo em Mac** (sem Boot Camp em Apple Silicon; só via VM Windows paga ou Power BI Service no navegador, com menos poder de transformação). Streamlit resolve em Python puro, no mesmo venv/dados já tratados. O dashboard não faz parte das entregas RA1 a RA3; o trabalho exploratório fica na branch `feat/ra2-analysis`.

**Notebook, não script solto**, pra Inspect/Prepare (e análises futuras) — formato escolhido pelo grupo pra facilitar correção e demonstração pra professora.

Ambiente: venv dedicado do projeto em `.venv/`, dependências travadas em `requirements.txt` (`pip freeze`).

## Decisões e dificuldades encontradas

- **Cabeçalho malformado no dataset principal** (dificuldade): `fronkongames/games.csv` tem 39 nomes de coluna no cabeçalho contra 40 campos por linha real — `"DiscountDLC count"` era a fusão de dois nomes que perderam o separador. Isso desalinhava quase todas as colunas nas 125.855 linhas (ex.: `Release date` vinha com valores de faixa de owners). Detectado por inspeção cruzada (`csv.reader` cabeçalho vs. primeira linha) e corrigido reconstruindo o cabeçalho. Detalhe completo com evidência em [`Notebooks/01_inspect_prepare.ipynb`](Notebooks/01_inspect_prepare.ipynb), seção "Problema 1".
- **Fontes catalogadas x fontes usadas**: o plano inicial era combinar os 3 datasets Kaggle (principal + 2 de cross-check/referência) e as 2 APIs ao vivo, para comparar histórico com tempo real. Nas entregas, os notebooks carregam só a base principal (`fronkongames`); as demais fontes ficaram catalogadas e exploradas fora do `master`.
- **P4 (histórico x ao vivo) não foi respondida com dado real**: o RA2 demonstra o processamento em fluxo com leituras simuladas a partir do `Peak CCU` real, e a telemetria ao vivo não foi coletada. Está registrado como limitação na seção 17 do notebook.
- **Limitação que condiciona RA2 e RA3**: ~84% do catálogo tem `Peak CCU` == 0 (ausência de telemetria, não pico zero; não imputado no RA1). Perguntas P1 a P3 valem só para o subconjunto com pico real.
- **Duplicatas de nome de jogo mantidas** (decisão, não erro): 1.593 títulos repetidos com `AppID` diferente (demos, remasters) — mantidos porque `AppID` é a chave real do dataset, não `Name`.
- **Exploração adiantada (RA2+)** — análise, validação cruzada com `waddahali`, reviews (`andrewmvd`), teste das APIs e dashboard — foi separada do RA1 e vive na branch `feat/ra2-analysis`.

## Estrutura de pastas

```
PJBL/
├── Dataset/          # CSVs originais + games_clean.csv (fora do git)
├── Notebooks/        # 01_inspect_prepare (RA1) + projeto_data_analytics (RA1 + RA2 + RA3, template da disciplina)
├── docs/             # RA1_Data_Analytics.docx, projeto_data_analytics_RA1_RA2_RA3.pdf (PDF do notebook, entrega RA1/RA2/RA3), roteiro_demo_RA2.md, roteiro_demo_RA3.md, template
├── tools/            # build_notebook.py (gera o notebook do projeto a partir do template) e gerar_pdf.sh (executa e exporta o PDF)
├── .venv/            # ambiente Python do projeto (fora do git)
└── requirements.txt  # dependências travadas
```

## Como rodar

Pré-requisitos: **Python 3.14** (o 3.15 não compila o `pyarrow`) e **Java 17** (o notebook do projeto usa PySpark 4.0.3).

```bash
# 1) ambiente
python3.14 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2) dados: salvar games.csv em Dataset/fronkongames/games.csv (Drive do grupo ou Kaggle, ver "Fontes de dados")

# 3) executar os notebooks do início ao fim
.venv/bin/jupyter nbconvert --to notebook --execute --inplace Notebooks/01_inspect_prepare.ipynb        # RA1, ~20 s
.venv/bin/jupyter nbconvert --to notebook --execute --inplace Notebooks/projeto_data_analytics.ipynb   # RA1 + RA2 + RA3, ~25 s
```

Como verificar: os dois comandos terminam sem erro; no notebook do projeto, a seção 6 imprime `125855 linhas x 42 colunas`, a seção 11 imprime `Streaming e batch coincidem nas 9 médias` e a seção 16.2 mostra a tabela de métricas (random forest no cenário A com R² 0,713).

O notebook do projeto é gerado por `tools/build_notebook.py`; para mudar texto ou código, edite o gerador e rode `bash tools/gerar_pdf.sh`, que regera o notebook, executa e exporta o PDF.

## Status atual

**RA1 (Inspect/Prepare):** `01_inspect_prepare.ipynb` executado do zero (7 problemas de qualidade, decisões justificadas, validação, `games_clean.csv`). Documentação da entrega em `docs/RA1_Data_Analytics.docx`.

**RA2 (Data Stream):** seções 8 a 12 de `Notebooks/projeto_data_analytics.ipynb`. Spark Structured Streaming, cenário A (dados estáticos + chegada simulada de registros artificiais): 45 leituras de jogadores simultâneos dos 3 jogos de maior `Peak CCU` (Counter-Strike 2, Dota 2, PUBG), chegando em 3 lotes por uma pasta monitorada. Janela **tumbling de 5 minutos**, agregação = **média de jogadores simultâneos** por janela e por jogo. Um `assert` confirma que o resultado do streaming é igual ao cálculo em batch (pandas). Entrega em PDF: `docs/projeto_data_analytics_RA1_RA2_RA3.pdf`; roteiro da demonstração: `docs/roteiro_demo_RA2.md`.

**RA3 (Análise e Machine Learning):** seções 13 a 17 de `Notebooks/projeto_data_analytics.ipynb`. Estatística descritiva (seção 13) no universo com telemetria (19.680 jogos com `Peak CCU` > 0, ou 15,6% do catálogo de 125.855), caracterizando assimetria extrema em `Peak CCU` (média 340 vs. mediana 3, razão de 113,4x; desvio-padrão de 9.304; amplitude de 1 a 1.013.936; 1% mais jogado concentra 82,1% do pico total), `owners_avg` (média 444.798 vs. mediana 35.000) e `Price` (média US$ 6,86 vs. mediana US$ 4,79; 11,1% gratuitos), com `Metacritic score` disponível em 15,3% dos jogos (média 75,9, mediana 77). Quatro visualizações (seção 14): histograma de `Peak CCU` (linear vs. log10), boxplot por gênero (medianas de 2 a 4; médias de 1.963 em Free To Play e 649 em Action contra 148 em Indie e 115 em Casual), dispersão de `owners_avg` x `Peak CCU` (Spearman 0,54, p ≈ 0) e mapa de calor de Spearman (Metacritic 0,39 e preço 0,20 com o pico). Amostragem e representatividade (seção 15): o catálogo é um censo histórico sem amostragem probabilística, com viés de sobrevivência no universo analisado (preço mediano de US$ 4,79 vs. US$ 1,99 dos jogos sem telemetria), viés temporal (jogos com telemetria caem de 33% em 2015 para 9% em 2025 e 0% em 2026) e baixa cobertura crítica, delimitando que as conclusões não devem ser generalizadas para todo o catálogo nem interpretadas como causalidade. Machine Learning (seção 16): regressão supervisionada para prever `log10(Peak CCU)` avaliada em split 80/20 (15.744 treino / 3.936 teste) comparando baseline da média, regressão linear e Random Forest (200 árvores, max_depth=12) em três cenários de features. No cenário A (todas as 15 features), a Random Forest alcança R² de 0,713 e MAE de 0,35 em log10 (erro típico de 2,2x no `Peak CCU`, contra 4,8x e R² 0 do baseline); no cenário B (sem `owners_avg`), mantém R² de 0,711 porque `log_avaliacoes` responde por 72,3% da importância; no cenário C (apenas características intrínsecas: preço, metacritic, ano, gênero), o R² cai para 0,234 (MAE 0,574), evidenciando que os atributos de cadastro, sem medidas de popularidade, explicam menos de 24% da variância. O ambiente conta com `scikit-learn` e `scipy` em `requirements.txt`. Conclusões (seção 17): fechamento das perguntas analíticas P1 a P4 e síntese das limitações. Roteiro da apresentação: `docs/roteiro_demo_RA3.md`.

O RA3 (seções 13 a 17 do notebook) já está no `master`. Só o trabalho além do RA3 (API e dashboard) fica fora, na branch `feat/ra2-analysis`.

**Ressalva**: as entregas foram conferidas contra os enunciados do RA1, do RA2 e do RA3 publicados no Canvas — não há visibilidade sobre orientações dadas verbalmente em sala que não estejam nos enunciados, nos slides ou no plano de ensino.
