# Guia de estudo do RA3 (apresentação de 18/11/2026)

Material de estudo pessoal. Todos os números foram conferidos com as saídas de `Notebooks/projeto_data_analytics.ipynb` (seções 13 a 16). O roteiro de fala é [roteiro_demo_RA3.md](roteiro_demo_RA3.md).

---

## 0. Mapa em uma página

- **Pergunta de pesquisa:** quais características de um jogo na loja Steam (preço, gênero, nota/reviews) se associam a um pico maior de jogadores simultâneos (`Peak CCU`)?
- **Subperguntas:** P1 preço, P2 gênero, P3 reviews e Metacritic, P4 histórico x ao vivo.
- **Universo do RA3:** 19.680 jogos com `Peak CCU` > 0 (15,6% dos 125.855 do catálogo).
- **História em uma frase:** a audiência é extremamente concentrada (o 1% do topo tem 82,1% do pico somado); preço, gênero e nota dizem pouco sozinhos; o modelo acerta bem (R² 0,71) só quando recebe medidas de popularidade acumulada, e cai para R² 0,23 com as características que o jogo tem antes de lançar.

---

## 1. Ponte com RA1 e RA2

| Etapa | O que entregou | Como o RA3 usa |
|---|---|---|
| **RA1** (inspecionar e preparar) | `df_limpo`: 125.855 jogos x 42 colunas, tipos corrigidos, `owners_avg` (ponto médio da faixa de donos do SteamSpy), datas convertidas | O RA3 parte de `df_limpo` e filtra `Peak CCU` > 0 |
| **RA2** (Data Stream) | Spark Structured Streaming, cenário A (dados estáticos + chegada simulada), janela tumbling de 5 min com média de jogadores por jogo, top 3 por `Peak CCU` (Counter-Strike 2, Dota 2, PUBG), 45 leituras com `random.Random(42)`, `assert` streaming = batch | Responde a parte "processamento ao vivo" da P4; no RA3 ela vira limitação, porque a telemetria ao vivo real não foi coletada |

Frase de transição para a fala: "No RA1 limpamos a base, no RA2 mostramos que dá para processar em fluxo; no RA3 perguntamos o que, nessa base, explica o pico de audiência."

---

## 2. Seção 13: estatística descritiva

### O que foi feito
Tabela com contagem, média, mediana, desvio-padrão, mínimo, máximo, amplitude, Q1, Q3, P95 e assimetria para `Price`, `Peak CCU`, `Metacritic score` e `owners_avg`. Mais a razão média/mediana e a concentração do top 1%.

### Números
| Variável | Média | Mediana | Desvio | Q1 a Q3 | P95 | Assimetria |
|---|---|---|---|---|---|---|
| `Peak CCU` | 340 | 3 | 9.304 | 1 a 15 | 328 | 84,17 |
| `owners_avg` | 444.798 | 35.000 | 3,19 mi | 10 mil a 150 mil | 1,5 mi | 29,05 |
| `Price` (US$) | 6,86 | 4,79 | 8,85 | 1,85 a 9,59 | 19,99 | 6,72 |
| `Metacritic score` | 75,9 | 77 | 9,2 | 71 a 82 | 89 | -1,15 |

- Razão média/mediana: `Peak CCU` 113x, `owners_avg` 12,7x, `Price` 1,4x, Metacritic 1,0x.
- Amplitude do `Peak CCU`: 1 a 1.013.936.
- Top 1% concentra 82,1% do `Peak CCU` somado. 11,1% são gratuitos. Metacritic existe em 15,3% (3.004 jogos).

### Conceitos
- **Média x mediana:** a média soma tudo e divide; um único jogo com 1 milhão de jogadores puxa a média para cima. A mediana é o valor do meio da fila ordenada e ignora o tamanho dos extremos. Quando as duas se afastam muito, a mediana descreve melhor o "jogo típico".
- **Desvio-padrão:** distância média dos valores em relação à média. 9.304 é 27x a média: sinal de que poucos valores enormes dominam.
- **Quartis e percentil:** Q1 = 25% dos jogos estão abaixo; Q3 = 75%; P95 = 95%. O miolo (Q1 a Q3) é só de 1 a 15 jogadores: a base é estreita e a variação vem da cauda.
- **Assimetria (skewness):** 0 é simétrico; positivo é cauda longa à direita. 84 é extremo. Metacritic negativo (-1,15): notas concentradas no alto, com poucas notas muito baixas.
- **Concentração:** "mercado de poucos vencedores". É a justificativa para tudo o que vem depois.

### Consequência (decore)
Escala log10 em `Peak CCU` e `owners_avg`, e correlação de Spearman em vez de Pearson.

---

## 3. Seção 14: visualizações

### 14.1 Histograma de `Peak CCU`
- Linear (cortado no P95): quase tudo na primeira barra, ilegível.
- log10: massa entre 1 e 100 jogadores (log 0 a 2), cauda até 6 (1 milhão). Linha da média (340) bem à direita da mediana (3).
- **log10 em uma frase:** cada unidade a mais é 10 vezes mais jogadores (log 2 = 100, log 3 = 1.000). Transforma multiplicação em soma, deixa a cauda legível.

### 14.2 Boxplot por gênero (8 mais frequentes)
| Gênero | Jogos | Mediana | Média |
|---|---|---|---|
| Free To Play | 1.557 | 4 | 1.963 |
| Action | 7.212 | 4 | 649 |
| RPG | 4.931 | 4 | 339 |
| Strategy | 5.045 | 4 | 314 |
| Simulation | 5.385 | 4 | 266 |
| Adventure | 7.887 | 3 | 256 |
| Indie | 11.819 | 2 | 148 |
| Casual | 6.673 | 2 | 115 |

- Medianas quase iguais (2 a 4). A diferença está na média, puxada por megassucessos (Counter-Strike, Dota 2, PUBG).
- **Frase-chave:** "gênero não muda o jogo típico, muda a chance de existir um campeão".
- Um jogo tem vários gêneros, por isso as contagens somam mais que 19.680 (`explode` dos gêneros).
- `showfliers=False`: outliers não desenhados para a caixa ficar legível; os números da tabela usam todos os jogos.

### 14.3 Dispersão `owners_avg` x `Peak CCU` (hexbin, ambos em log10)
- Spearman 0,54 (p ≈ 0): relação positiva moderada.
- Nuvem larga: com 1,5 milhão de donos, `Peak CCU` vai de 4 (P5) a 2.549 (P95). Posse é necessária, não suficiente.
- Região mais densa: ~10 mil donos com 1 a 2 jogadores (7.779 jogos, 40%).
- **Hexbin:** em vez de 19.680 pontos sobrepostos, conta quantos jogos caem em cada hexágono (cor em escala log).

### 14.4 Mapa de calor de Spearman
| Par | Spearman |
|---|---|
| `Peak CCU` x `owners_avg` | 0,54 |
| `Peak CCU` x Metacritic | 0,39 |
| `Peak CCU` x `Price` | 0,20 |
| Metacritic x `owners_avg` | 0,26 |
| Metacritic x `Price` | 0,25 |
| `Price` x `owners_avg` | -0,08 |

- **Spearman x Pearson:** Pearson mede relação linear entre os valores e é dominado por outliers. Spearman troca os valores pela posição no ranking (postos) e mede se "quem é maior em X tende a ser maior em Y" (relação monotônica). Com assimetria 84, Pearson seria distorcido pelos poucos gigantes.
- Escala de leitura (convenção comum): < 0,3 fraca, 0,3 a 0,7 moderada, > 0,7 forte.
- Correlação com Metacritic vale só para os 3.004 jogos com crítica.

---

## 4. Seção 15: amostragem e representatividade

- **Origem:** dataset do Kaggle `fronkongames/steam-games-dataset`, coleta da loja Steam. É praticamente um **censo** do catálogo, não amostra sorteada; nenhuma técnica de amostragem foi aplicada.
- **Comparação de universos:**

| Grupo | Jogos | Preço médio | Preço mediano |
|---|---|---|---|
| Sem telemetria (`Peak CCU` = 0) | 106.175 | 4,43 | 1,99 |
| Com telemetria (`Peak CCU` > 0) | 19.680 | 6,86 | 4,79 |

- **Vieses:**
  1. **Sobrevivência/telemetria:** só entram jogos que tiveram audiência medida. Eles são mais caros e mais estabelecidos. Conclusões valem para jogos "que apareceram".
  2. **Temporal:** proporção com telemetria cai de 33% (2015) para 9% (2025) e 0% (2026). Jogos recentes ainda não acumularam histórico, e a base é uma fotografia do momento da coleta.
  3. **Medida:** `Peak CCU` é um pico histórico único, não série temporal; `owners_avg` é ponto médio de faixa do SteamSpy (discretizado).
  4. **RA2:** as leituras do streaming são simuladas.
- **Conclusão da seção:** a análise é válida para o universo com telemetria, sem generalizar para todo o catálogo e sem falar em causalidade.

---

## 5. Seção 16: Machine Learning

### 16.1 Problema
- **Tipo:** aprendizado supervisionado, **regressão** (alvo numérico contínuo).
- **Alvo:** `log10(Peak CCU)`. Motivos: assimetria 84; estabiliza a variância dos resíduos; o erro passa a ser em ordens de grandeza (multiplicativo), o que faz sentido quando o alvo vai de 1 a 1 milhão.
- **Features (15 no cenário A):**
  - `Price`
  - `metacritic` (nulo preenchido pela mediana do treino) + `tem_metacritic` (indicador 0/1 de presença)
  - `prop_positivas` (proporção de reviews positivas; 0,5 quando não há reviews)
  - `log_avaliacoes` (log10 do total de reviews + 1)
  - `ano` de lançamento (nulo pela mediana do treino)
  - 8 indicadores `genero_*` (0/1)
  - `log_owners` (log10 de `owners_avg`)
- **Split:** `train_test_split(test_size=0.2, random_state=42)`: 15.744 treino, 3.936 teste.
- **Sem vazamento na imputação:** o split é feito **antes** de calcular a mediana do Metacritic e do ano; a mediana vem só do treino. Se viesse da base inteira, informação do teste "vazaria" para o treino.

### Os três modelos
- **Baseline `DummyRegressor(strategy="mean")`:** sempre prevê a média do treino. É a régua mínima: qualquer modelo útil precisa ganhar dele. R² = 0 por definição.
- **`LinearRegression`:** soma ponderada das features (uma reta/hiperplano). Simples e interpretável, mas não capta curvas nem interações.
- **`RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)`:** 200 árvores de decisão, cada uma treinada numa amostra sorteada dos dados e com subconjuntos de features; a previsão é a média das árvores. Capta relações não lineares e interações (ex.: gratuito + Action + ano recente) e é robusto a outliers. `max_depth=12` limita a profundidade para reduzir overfitting.

### Métricas (todas em unidades de log10)
- **MAE:** erro absoluto médio. MAE 0,346 em log10 significa errar, em média, por um fator de 10^0,346 ≈ **2,2x** no `Peak CCU` (para mais ou para menos).
- **RMSE:** raiz do erro quadrático médio; pune mais os erros grandes. RMSE > MAE indica alguns erros grandes.
- **R²:** fração da variância do alvo explicada pelo modelo. 0 = igual a prever a média; 1 = perfeito; negativo = pior que a média.

### 16.2 Resultados
| Cenário | Modelo | MAE | RMSE | R² |
|---|---|---|---|---|
| A) todas (15) | baseline | 0,679 | 0,869 | 0,000 |
| | linear | 0,437 | 0,575 | 0,562 |
| | random forest | **0,346** | **0,465** | **0,713** |
| B) sem `owners_avg` (14) | baseline | 0,679 | 0,869 | 0,000 |
| | linear | 0,475 | 0,618 | 0,495 |
| | random forest | 0,346 | 0,467 | 0,711 |
| C) só intrínsecas (12) | baseline | 0,679 | 0,869 | 0,000 |
| | linear | 0,597 | 0,781 | 0,193 |
| | random forest | 0,574 | 0,761 | 0,234 |

Fatores de erro: baseline 10^0,679 ≈ 4,8x; RF A ≈ 2,2x; RF C ≈ 3,7x.

**Importância das features (RF, cenário B):** `log_avaliacoes` 0,723; `ano` 0,080; `Price` 0,057; `prop_positivas` 0,047; `genero_Indie` 0,019; `genero_Strategy` 0,016; `genero_Adventure` 0,010; `genero_Action` 0,010. Importância = quanto cada feature reduz o erro (impureza) nas divisões das árvores, somado e normalizado.

### Leitura dos cenários (o ponto mais importante do RA3)
- **A:** RF ganha da linear (0,71 x 0,56) porque a relação não é linear e há interações.
- **A para B:** tirar `owners_avg` quase não muda a floresta (0,713 para 0,711), porque `log_avaliacoes` carrega a mesma informação (popularidade acumulada) e vira 72% da importância. Na linear a queda aparece (0,56 para 0,50).
- **Vazamento parcial:** donos e número de reviews só existem **depois** que o jogo fez sucesso. Usá-los para "prever" o pico é quase prever o alvo com um parente do alvo. Bom para estimar a ordem de grandeza de um jogo já conhecido, inútil para um lançamento.
- **C:** o teste honesto "pré-lançamento" (preço, Metacritic e indicador, ano, 8 gêneros). R² 0,23: o jogo em si explica só cerca de 23% da variância.
- **0,71 - 0,23 = 0,48:** quanto do poder preditivo vem de popularidade acumulada.
- Gráfico previsto x real (cenário B): pontos perto da diagonal vermelha = bons; espalhamento maior nos jogos pequenos.

### Limitações do modelo
Split único 80/20 (sem validação cruzada), hiperparâmetros fixos (sem busca), só jogos com telemetria, Metacritic imputado em 84,7% dos casos, `owners_avg` discretizado.

---

## 6. Seção 17: conclusões (P1 a P4)

- **P1 Preço:** associação fraca (Spearman 0,20). Preço quase não se relaciona com donos (-0,08).
- **P2 Gênero:** mediana quase igual entre gêneros (2 a 4); gênero muda a chance de um campeão (Free To Play e Action).
- **P3 Reviews e Metacritic:** Metacritic moderado (0,39), mas só em 15,3% da base. Volume de reviews é a variável mais forte do modelo, mas é popularidade acumulada. Intrínsecas juntas: ~23% da variância.
- **P4 Histórico x ao vivo:** o RA2 mostrou o processamento contínuo em janelas de 5 min com dados simulados; telemetria ao vivo real não foi coletada, fica como limitação.
- **Próximos passos:** validação cruzada e busca de hiperparâmetros, features de texto (descrição, tags), série temporal real de `Peak CCU` (lançamento e retenção).

---

## 7. Banca: perguntas e respostas curtas

**Do roteiro**
- *Por que log?* Assimetria 84, valores de 1 a 1 milhão. O log10 lineariza a escala, estabiliza a variância dos resíduos e torna o erro multiplicativo (ordens de grandeza).
- *Por que random forest?* Capta não linearidade e interações entre gêneros, preço e ano; subiu o R² de 0,56 (linear) para 0,71.
- *Vazamento de `owners_avg` e reviews?* São medidas acumuladas depois do lançamento; prever pico com elas é quase prever o alvo com o próprio alvo. Por isso existem os cenários B e C.
- *Viés de telemetria?* 84,4% da base tem `Peak CCU` = 0 por falta de medição; os 15,6% restantes são mais caros (mediana US$ 4,79 x 1,99) e visíveis: viés de sobrevivência.
- *O que significa o cenário C?* O teste pré-lançamento honesto: só atributos de cadastro, R² 0,23.
- *E a P4?* Fora do escopo do RA3; o RA2 só simulou o fluxo; registrado como limitação na seção 17.
- *Limitações?* Base estática, split único, hiperparâmetros fixos, Metacritic ausente em 84,7%, `owners_avg` em faixas.

**Armadilhas extras**
- *Por que não Pearson?* Pearson é sensível a outliers e só mede relação linear; com a cauda extrema, poucos jogos dominariam o coeficiente. Spearman usa postos e mede relação monotônica.
- *R² 0,71 é bom?* Para o cenário A é alto, mas é inflado pela popularidade acumulada. O número relevante para "o que o jogo diz sobre si" é 0,23.
- *Por que o baseline tem R² 0?* Porque prever a média é exatamente a referência do R². O "-0,000" da tabela é arredondamento: a média do treino difere um pouco da média do teste.
- *Por que não validação cruzada?* Escopo de "aplicação simples" do enunciado; está declarado como limitação e próximo passo. A CV mostraria quanto as métricas variam entre divisões diferentes.
- *Correlação implica causa?* Não. É estudo observacional sobre um censo filtrado; conclusões são de associação.
- *Por que imputar Metacritic pela mediana e criar `tem_metacritic`?* A mediana é robusta (a distribuição é assimétrica à esquerda) e o indicador deixa o modelo distinguir "nota real" de "nota preenchida"; ter crítica já é sinal de visibilidade.
- *Por que a mediana do treino e não da base toda?* Para não vazar informação do teste para o treino.
- *O que é overfitting e como evitaram?* Modelo decorar o treino e falhar em dado novo. Avaliação só no teste nunca visto, `max_depth=12` e média de 200 árvores. Não medimos o desempenho no treino, então a distância treino x teste não foi quantificada.
- *Por que regressão e não classificação?* O alvo é numérico contínuo; classificação (ex.: "sucesso sim/não") exigiria um limiar arbitrário.
- *Como prever um lançamento de verdade?* Só com features disponíveis antes do lançamento (cenário C) mais sinais de pré-lançamento (wishlists, seguidores, trailer, texto da descrição e tags).
- *O que o `random_state=42` garante?* Reprodutibilidade: mesmo split e mesma floresta a cada execução.
- *Por que 8 gêneros?* Os mais frequentes; o resto tem poucos jogos e geraria colunas quase vazias.

---

## 8. Cola de números

| Item | Valor |
|---|---|
| Catálogo / universo | 125.855 / 19.680 (15,6%) |
| Sem telemetria | 106.175 (84,4%) |
| `Peak CCU` média / mediana / razão | 340 / 3 / 113x |
| Desvio / assimetria / máx | 9.304 / 84,17 / 1.013.936 |
| Q1, Q3, P95 | 1, 15, 328 |
| Top 1% concentra | 82,1% |
| Preço média / mediana / gratuitos | US$ 6,86 / 4,79 / 11,1% |
| Metacritic cobertura / média / mediana | 15,3% (3.004) / 75,9 / 77 |
| Spearman CCU x donos / meta / preço | 0,54 / 0,39 / 0,20 |
| Preço x donos | -0,08 |
| Preço mediano sem x com telemetria | US$ 1,99 x 4,79 |
| Telemetria 2015 / 2025 / 2026 | 33% / 9% / 0% |
| Treino / teste | 15.744 / 3.936 |
| Baseline MAE / fator | 0,679 / 4,8x |
| RF A R² / MAE / fator | 0,713 / 0,346 / 2,2x |
| Linear A R² | 0,562 |
| RF B R² / `log_avaliacoes` | 0,711 / 72,3% |
| Linear B R² | 0,495 |
| RF C R² / MAE | 0,234 / 0,574 |
| Linear C R² | 0,193 |

## 9. Tempo da fala (5 min)
Problema 0:45, descritiva e gráficos 1:15, amostragem 0:45, ML 1:30, conclusões 0:45. Ensaiar com cronômetro pelo menos duas vezes.
