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

**Tipo de analytics:** **descritivo** (perfil do catálogo — distribuição de preço, gênero, nota) e **diagnóstico** (o que diferencia jogos com pico de jogadores alto dos demais). Não há componente preditivo nem prescritivo nesta fase do projeto.

## Fontes de dados

| Fonte (origem) | Formato | Registros | Principais atributos | Relação com o problema |
|---|---|---|---|---|
| [fronkongames/steam-games-dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) (Kaggle) | CSV | 125.855 linhas × 40 colunas (42 após preparo) | `AppID`, `Name`, `Release date`, `Price`, `Peak CCU`, `Estimated owners`, `Positive`/`Negative`, `Metacritic score`, `Genres`, `Tags` | **Base principal**: contém todas as variáveis das perguntas 1 a 3 |
| [srgiomanhes/steam-games-dataset-2025](https://www.kaggle.com/datasets/srgiomanhes/steam-games-dataset-2025) (Kaggle) | CSV | 71.429 × 21 | `steam_appid`, `name`, `genres`, `price_initial (USD)`, `total_positive`/`total_negative`, `metacritic` | Checagem de consistência de preço e reviews da base principal |
| [waddahali/top-1000-steam-games-2024-2026](https://www.kaggle.com/datasets/waddahali/top-1000-steam-games-20242026) (Kaggle) | CSV | 1.000 × 12 | `AppID`, `Price_USD`, `Primary_Genre`, `All_Tags`, `Review_Score_Pct`, `24h_Peak_Players` | Validação cruzada de `Peak CCU` e preço (ver `Notebooks/03_top1000_reference.ipynb`) |
| [andrewmvd/steam-reviews](https://www.kaggle.com/datasets/andrewmvd/steam-reviews/versions/3) (Kaggle) | CSV (2,16 GB) | 6.417.106 | texto e voto de review por `app_id` | **Fora do RA1** (só explorado, ver `Notebooks/04_reviews_exploration.ipynb`) |
| [Steam Web API](https://partner.steamgames.com/doc/webapi_overview) + [SteamSpy API](https://steamspy.com/api.php) | JSON (API) | por `appid` consultado | jogadores atuais, preço atual | Pergunta 4 (dado ao vivo); teste em [`API/README.md`](API/README.md), RA2+ |

**Ingestão (RA1):** os CSVs não vão pro GitHub (limite de 100 MB/arquivo). Para reproduzir: `pip install -r requirements.txt`, configurar `~/.kaggle/kaggle.json` e rodar `kaggle datasets download -d fronkongames/steam-games-dataset -p Dataset/fronkongames --unzip`. O notebook `01_inspect_prepare.ipynb` valida a presença de `Dataset/fronkongames/games.csv` e gera `games_clean.csv`.

## Ferramentas — decisão e por quê

**Pandas, não Spark/Hadoop.** O maior dataset (~125 mil linhas, dezenas/poucas centenas de MB) processa em memória em segundos numa máquina só. Spark/Hadoop só compensam em volume GB–TB ou processamento distribuído — seriam over-engineering aqui, e é literalmente o que a Aula 2 já ensina.

**Streamlit, não Power BI.** Decisão original era Power BI, revertida ao descobrir que **Power BI Desktop não roda nativo em Mac** (sem Boot Camp em Apple Silicon; só via VM Windows paga ou Power BI Service no navegador, com menos poder de transformação). Streamlit resolve em Python puro, no mesmo venv/dados já tratados, com a API ao vivo integrada direto no código.

**Notebook, não script solto**, pra Inspect/Prepare/Analysis — formato escolhido pelo grupo pra facilitar correção e demonstração pra professora.

Ambiente: venv dedicado do projeto em `.venv/`, dependências travadas em `requirements.txt` (`pip freeze`).

## Decisões e dificuldades encontradas

- **Cabeçalho malformado no dataset principal** (dificuldade): `fronkongames/games.csv` tem 39 nomes de coluna no cabeçalho contra 40 campos por linha real — `"DiscountDLC count"` era a fusão de dois nomes que perderam o separador. Isso desalinhava quase todas as colunas nas 125.855 linhas (ex.: `Release date` vinha com valores de faixa de owners). Detectado por inspeção cruzada (`csv.reader` cabeçalho vs. primeira linha) e corrigido reconstruindo o cabeçalho. Detalhe completo com evidência em [`Notebooks/01_inspect_prepare.ipynb`](Notebooks/01_inspect_prepare.ipynb), seção "Problema 1".
- **Endpoint `GetAppList` da Steam Web API descontinuado** (dificuldade): ver [`API/README.md`](API/README.md) — não dá mais pra listar todos os apps via API, só por `appid` específico, usando os datasets do Kaggle como lista de referência.
- **Decisão de combinar fontes em vez de escolher uma só**: o grupo optou por usar os 3 datasets Kaggle (principal + 2 de cross-check/referência) e as 2 APIs ao vivo, não um dataset único — o diferencial do projeto é justamente comparar histórico com tempo real no dashboard.
- **Limitação registrada na análise**: ~84% do catálogo tem `Peak CCU` == 0 (sem telemetria de pico), então a análise diagnóstica (o que diferencia jogos com pico alto) vale só pro subconjunto (~16%) com dado real de pico, não pro catálogo inteiro. Documentado em [`Notebooks/02_analysis_visualization.ipynb`](Notebooks/02_analysis_visualization.ipynb).
- **Duplicatas de nome de jogo mantidas** (decisão, não erro): 1.593 títulos repetidos com `AppID` diferente (demos, remasters) — mantidos porque `AppID` é a chave real do dataset, não `Name`.
- **Exploração inicial do dataset `andrewmvd` (reviews)**: passada completa em chunks nos 6.417.106 registros (2,16 GB) leva menos de 30s — viável processar o arquivo inteiro sem Spark. O dataset já traz um rótulo pronto de sentimento (`review_score`: 82% recomendado / 18% não recomendado), o que tornaria uma eventual extensão mais um exercício de classificação supervisionada do que sentiment analysis do zero. Achado de qualidade: o texto literal `"Early Access Review"` é inserido pela própria Steam (não pelo usuário) quando o jogo é Early Access e o usuário não escreveu nada — isso inflava a taxa de duplicata exata pra ~28% e precisaria ser filtrado antes de qualquer NLP. Limitação de escopo: só 9.972 `AppID` distintos têm review aqui, contra 125.855 da base principal — a extensão só cobriria ~7% do catálogo. Detalhe completo em [`Notebooks/04_reviews_exploration.ipynb`](Notebooks/04_reviews_exploration.ipynb).
- **Dataset `waddahali` (top 1000) explorado — serve como validação cruzada, não como fonte extra**: 88% de overlap por `AppID` com a base principal (os 12% restantes são majoritariamente lançamentos 2026 ainda não coletados na base principal). Nos 879 jogos em comum, `Peak CCU` tem correlação de **0,9999** entre as duas fontes coletadas independentemente — reforça que o pico de jogadores é a variável mais sólida da análise diagnóstica de `02_analysis_visualization.ipynb`, não um artefato de uma única coleta. Preço (0,74) e owners estimados (0,64) têm correlação mais fraca, esperado por metodologias/momentos de coleta diferentes. Detalhe em [`Notebooks/03_top1000_reference.ipynb`](Notebooks/03_top1000_reference.ipynb).

## Estrutura de pastas

```
PJBL/
├── Dataset/          # CSVs originais + games_clean.csv (fora do git)
├── API/              # teste das APIs ao vivo + README com o achado do 404
├── Notebooks/        # 01_inspect_prepare (RA1), 02..04 exploração/análise (RA2+)
├── Dashboard/         # app.py (Streamlit)
├── .venv/            # ambiente Python do projeto
└── requirements.txt  # dependências travadas
```

## Como rodar

```bash
# Notebooks (Inspect/Prepare, Analysis/Visualization)
.venv/bin/jupyter lab Notebooks/

# Dashboard
cd Dashboard && ../.venv/bin/streamlit run app.py
```

## Status atual (07/10/2026)
**RA1:** `01_inspect_prepare.ipynb` executado do zero (7 problemas de qualidade, decisões justificadas, validação, `games_clean.csv`). Pendente: documento `.docx` do template e validação das perguntas com a professora.

**Adiantado (RA2+, fora do escopo do RA1):** `02_analysis_visualization`, `03_top1000_reference`, `04_reviews_exploration` e `Dashboard/`.

**Ressalva**: alinhamento verificado contra o conteúdo dos slides de Aula 1 e Aula 2 no Canvas — não há visibilidade sobre orientações dadas verbalmente em sala que não estejam nos slides ou no plano de ensino.
