# PJBL — Data Analytics (Steam)

## Grupo
Lucas Stopinski da Silva, Lucas Bruno e Silva.

## Contexto e pergunta de pesquisa
Contexto: jogos, especificamente a plataforma **Steam**.

Pergunta inicial: *Quais características de um jogo na Steam (preço, gênero/tags, nota de review) estão associadas a maior pico de jogadores simultâneos, e como o catálogo histórico se compara ao comportamento ao vivo dos jogos mais jogados agora?*

Dados necessários pra responder: catálogo de jogos com preço, gênero/tags, nota de review e pico de jogadores (histórico) + dado de jogadores/preço atual por jogo (ao vivo).

**Classificação dos dados:** majoritariamente **estruturado** — os 4 datasets do Kaggle são tabulares (CSV) e as duas APIs (Steam Web API, SteamSpy) retornam JSON estruturado por campo. Não há dado não-estruturado no projeto (não usamos texto livre de review nem imagem/vídeo).

**Tipo de analytics:** **descritivo** (perfil do catálogo — distribuição de preço, gênero, nota) e **diagnóstico** (o que diferencia jogos com pico de jogadores alto dos demais). Não há componente preditivo nem prescritivo nesta fase do projeto.

## Fontes de dados

| Fonte | Papel |
|---|---|
| [fronkongames/steam-games-dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) | Base principal, ~125 mil jogos — usada pra Inspect/Prepare e Analysis |
| [srgiomanhes/steam-games-dataset-2025](https://www.kaggle.com/datasets/srgiomanhes/steam-games-dataset-2025) | Cross-check de consistência da base principal |
| [waddahali/top-1000-steam-games-2024-2026](https://www.kaggle.com/datasets/waddahali/top-1000-steam-games-20242026) | Referência validada/limpa, ainda não explorada em profundidade |
| [andrewmvd/steam-reviews](https://www.kaggle.com/datasets/andrewmvd/steam-reviews/versions/3) | Reviews em texto — baixado, fora de escopo até aqui (fica pra uma eventual extensão com análise de sentimento) |
| [Steam Web API](https://partner.steamgames.com/doc/webapi_overview) + [SteamSpy API](https://steamspy.com/api.php) | Dado ao vivo, alimenta a aba "Dado ao vivo" do dashboard — ver [`API/README.md`](API/README.md) |

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

## Estrutura de pastas

```
PJBL/
├── Dataset/          # CSVs originais + games_clean.csv (tratado)
├── API/              # teste das APIs ao vivo + README com o achado do 404
├── Notebooks/        # 01_inspect_prepare, 02_analysis_visualization
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

## Status atual (04/09/2026)
Inspect/Prepare e Analysis/Visualization concluídos e executados com evidência real. Dashboard funcional com histórico + dado ao vivo. Pendente: exploração do dataset `waddahali` (referência limpa) e do dataset de reviews (`andrewmvd`, ainda fora de escopo).

**Ressalva**: alinhamento verificado contra o conteúdo dos slides de Aula 1 e Aula 2 no Canvas — não há visibilidade sobre orientações dadas verbalmente em sala que não estejam nos slides ou no plano de ensino.
