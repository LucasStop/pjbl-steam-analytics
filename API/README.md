# APIs Steam — teste de acesso

Objetivo: avaliar se dá pra complementar os datasets históricos do Kaggle com dado "ao vivo" direto da Steam, sem depender só de arquivos estáticos. Evidência completa em [`steam_api_test.ipynb`](steam_api_test.ipynb).

## APIs testadas

**Steam Web API** (`api.steampowered.com`) — dados oficiais da Valve: notícias por jogo e detalhes de loja (preço, gêneros, data de lançamento). Pública, sem API key.

**Steam Store API** (`store.steampowered.com/api/appdetails`) — detalhes completos de um app específico (nome, preço, gêneros, categorias, data de lançamento). Pública, sem key.

**SteamSpy** (`steamspy.com/api.php`) — dados agregados de comunidade: owners estimados, peak CCU nas últimas 24h, contagem de reviews positivas/negativas. Pública, sem key.

No projeto, essas três servem para complementar o dataset histórico do Kaggle com um recorte atual (preço/popularidade/reviews de hoje), não para substituí-lo.

## Achado: `GetAppList/v2` fora do ar

O método clássico pra listar **todos** os apps da Steam de uma vez, `ISteamApps/GetAppList/v2`, retornou **404** no teste (04/09/2026). Não é erro de código — o endpoint parece ter sido descontinuado pela Valve (não aparece mais listado em `ISteamWebAPIUtil/GetSupportedAPIList`).

Contorno usado, ambos funcionando sem key:
- `ISteamNews/GetNewsForApp` — notícias de um jogo específico.
- `store.steampowered.com/api/appdetails?appids=<id>` — detalhes de um jogo específico (nome, preço, gêneros, data de lançamento).

SteamSpy (`steamspy.com/api.php?request=appdetails&appid=<id>`) funciona normalmente e retorna owners estimados, peak CCU 24h e contagem de reviews.

## Implicação prática pro projeto

Sem `GetAppList`, não dá mais pra descobrir jogos novos só pela API — todo endpoint que sobrou (`GetNewsForApp`, `appdetails`, SteamSpy) exige um `appid` específico. Ingestão ao vivo, portanto, tem que ser feita **por appid**, usando como referência a lista de jogos já presente nos datasets do Kaggle (ex.: `fronkongames/games.csv`), não por varredura direta da Steam.
