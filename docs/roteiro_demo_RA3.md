# Roteiro da demonstração RA3 (5 minutos)

Notebook: `Notebooks/projeto_data_analytics.ipynb`. Antes de começar: abrir o notebook já executado e posicionar na seção 13.

1. **Problema e universo Peak CCU > 0 (0:45)** — Catálogo da Steam com 125.855 jogos (`df_limpo` do RA1), mas 84,4% (106.175) não possuem registro de pico. O universo do RA3 restringe-se aos jogos com telemetria real (`Peak CCU` > 0): **19.680 jogos** (15,6% do catálogo). Pergunta central: quais características da loja (preço, gênero, nota/reviews) se associam ao pico de audiência simultânea?
2. **Estatística descritiva e gráficos (1:15)** —
   - Distribuição de `Peak CCU` (seções 13 e 14.1): assimetria extrema (84,17). Média de 340 contra mediana de 3 jogadores (razão de 113 vezes); desvio-padrão de 9.304 (27x a média); o 1% mais jogado concentra **82,1%** de toda a audiência. Exige escala log10 e correlação de Spearman. Preço médio US$ 6,86 (mediana US$ 4,79; 11,1% gratuitos); Metacritic cobre só 15,3% do universo (3.004 jogos; média 75,9, mediana 77).
   - Gêneros (14.2): medianas quase idênticas entre os 8 gêneros principais (2 a 4 jogadores). A diferença surge na média/cauda: Free To Play (1.963) e Action (649) puxados por poucos megassucessos, contra Indie (148) e Casual (115). Gênero não muda o jogo típico, muda a chance de um campeão.
   - Dispersão e correlação (14.3 e 14.4): Spearman de `Peak CCU` é moderada com `owners_avg` (0,54) e `Metacritic score` (0,39), e fraca com `Price` (0,20). Preço vs donos é nulo (-0,08).
3. **Amostragem e vieses (0:45)** —
   - Origem: censo do catálogo Steam via Kaggle (125.855 jogos), sem amostragem probabilística.
   - Viés de telemetria/sobrevivência: os 19.680 jogos com `Peak CCU` > 0 não são amostra aleatória; são jogos mais caros (mediana US$ 4,79 contra US$ 1,99 dos jogos sem telemetria) e mais estabelecidos.
   - Viés temporal: proporção com telemetria cai de 33% (2015) para 9% (2025) e 0% (2026), pois títulos recentes ainda não acumularam histórico e a base reflete o momento da coleta.
4. **Machine Learning (1:30)** —
   - Setup (seção 16.1): regressão supervisionada para estimar `log10(Peak CCU)`. Split 80/20 com seed 42 (15.744 treino / 3.936 teste). Metacritic imputado pela mediana do treino (77,0).
   - Comparação dos 3 cenários (16.2):
     - Baseline (prever a média): MAE 0,679, RMSE 0,869, R² 0,000 (fator de erro de 4,8x).
     - Cenário A (todas as 15 features): Random Forest atinge R² 0,713 e MAE 0,346 (erro de 2,2x no `Peak CCU`), superando a Regressão Linear (R² 0,562).
     - Cenário B (sem `owners_avg`): Random Forest mantém R² 0,711 e MAE 0,346, pois `log_avaliacoes` supre a informação e responde por 72,3% da importância do modelo.
     - Cenário C (só características intrínsecas: preço, gênero, ano, nota): R² despenca para 0,234 no Random Forest (MAE 0,574) e 0,193 na Regressão Linear.
   - Leitura do modelo: o alto poder preditivo de A e B decorre de popularidade acumulada pós-lançamento, e não de capacidade preditiva pré-lançamento.
5. **Conclusões vs P1-P4 (0:45)** —
   - P1 (Preço): associação fraca com `Peak CCU` (Spearman 0,20).
   - P2 (Gênero): não diferencia o jogo típico (mediana 2 a 4), mas define a probabilidade de campeões de audiência.
   - P3 (Reviews e Metacritic): Metacritic tem correlação moderada (0,39), mas restrita a 15,3% da base. Características intrínsecas explicam apenas 23% da variância de `Peak CCU`; o restante é popularidade acumulada ou fatores externos à loja.
   - P4 (Histórico x Ao vivo): o RA2 demonstrou processamento contínuo em janelas de 5 min com dados simulados, mas a telemetria ao vivo real não foi coletada, permanecendo como limitação.

Perguntas prováveis: por que log? (variável extremamente assimétrica, assimetria 84, variando de 1 a 1 milhão; o log10 lineariza a escala, estabiliza a variância dos resíduos e converte o erro em ordens de grandeza multiplicativas); por que random forest? (captura relações não lineares e interações complexas entre múltiplos gêneros, preço e ano, superando a regressão linear de R² 0,56 para 0,71); vazamento de owners_avg e reviews? (ambas são métricas acumuladas ao longo do ciclo de vida pós-lançamento; usá-las para estimar pico é quase prever o alvo com o próprio alvo, inviável para previsão de novos lançamentos); viés de telemetria? (84,4% da base tem `Peak CCU` = 0 por falta de medição na loja; o recorte de 15,6% seleciona jogos com maior visibilidade e preço mediano de US$ 4,79 vs US$ 1,99, configurando viés de sobrevivência); o que significa o cenário C? (é o teste honesto pré-lançamento: quanto os atributos intrínsecos de cadastro explicam do pico de audiência — resposta: apenas 23% da variância); limitações? (base estática sem série temporal contínua; split único 80/20 sem validação cruzada; hiperparâmetros fixos; Metacritic ausente em 84,7% dos jogos; `owners_avg` discretizado em faixas pelo SteamSpy).
