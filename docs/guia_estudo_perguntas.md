# Guia de estudo para a arguição (RA1 + RA2)

Material de estudo, não é entrega. Todos os números abaixo foram conferidos nas saídas do notebook executado (`Notebooks/projeto_data_analytics.ipynb`). Regra de ouro na banca: responda o que foi perguntado, em duas ou três frases, e admita o limite quando existir. A professora avalia compreensão, não perfeição.

## 1. Cola de números

**Dados (RA1)**
- Fonte: `fronkongames/steam-games-dataset` (Kaggle), `games.csv`, 401 MB, **125.855 jogos × 40 campos**. Depois do preparo: **125.855 × 42** (40 colunas, menos `Movies`, mais `owners_min`, `owners_max` e `owners_avg`).
- Cabeçalho: **39 nomes para 40 campos**; `"DiscountDLC count"` era `Discount` + `DLC count` sem separador. Leitura ingênua dava 125.855 × 39 e `AppID` com 1 nulo.
- `Movies`: 100% vazia, removida.
- `Metacritic score` == 0 em **121.597** linhas (96,6%) → virou NaN; sobram **4.258** notas reais (3,4%).
- `Peak CCU` == 0 em **84,4%** dos jogos (sem telemetria, não "pico zero"); ficaram sem imputação.
- **1.593** nomes repetidos com `AppID` diferente (demos, remasters): mantidos. Duplicatas exatas e de `AppID`: 0.
- Maior pico: Counter-Strike 2, `Peak CCU` = 1.013.936.

**Streaming (RA2)**
- Top 3 por `Peak CCU`: Counter-Strike 2 (1.013.936), Dota 2 (623.941), PUBG: BATTLEGROUNDS (314.682).
- **45 leituras** = 3 jogos × 15 minutos, a partir de 2026-10-21 14:00, `random.Random(42)`, fração do pico = 0,70 + 0,02 × minuto ± 0,03, nunca acima do pico.
- **3 lotes**: lote 1 = minutos 0 a 6 (21 leituras), lote 2 = minutos 7 a 11 (15), lote 3 = minutos 12 a 14 (9).
- Spark 4.0.3, `local[2]`, `shuffle.partitions=2`, fuso `America/Sao_Paulo`.

| Janela | Jogo | após lote 1 | após lote 2 | após lote 3 |
|---|---|---|---|---|
| 14:00-14:05 | Counter-Strike 2 | 741.931 | 741.931 | 741.931 |
| 14:00-14:05 | Dota 2 | 452.476 | 452.476 | 452.476 |
| 14:00-14:05 | PUBG | 232.973 | 232.973 | 232.973 |
| 14:05-14:10 | Counter-Strike 2 | 832.067 | 859.085 | 859.085 |
| 14:05-14:10 | Dota 2 | 490.922 | 518.504 | 518.504 |
| 14:05-14:10 | PUBG | 258.622 | 263.377 | 263.377 |
| 14:10-14:15 | Counter-Strike 2 | (não existe) | 946.415 | 964.231 |
| 14:10-14:15 | Dota 2 | (não existe) | 569.813 | 588.157 |
| 14:10-14:15 | PUBG | (não existe) | 287.194 | 294.198 |

História em uma frase: a janela 14:00 fecha no lote 1 e não muda mais; a 14:05 está pela metade no lote 1 e muda no lote 2; a 14:10 nasce no lote 2 e muda no lote 3.

## 2. Perguntas prováveis sobre o RA1

**Qual era o problema mais grave nos dados e como vocês acharam?** O cabeçalho tinha 39 nomes e as linhas 40 campos. Comparamos o cabeçalho com a primeira linha usando `csv.reader` e vimos que `Release date` trazia faixas de owners (`'200000 - 500000'`). Corrigimos inserindo `Discount` antes de `DLC count`.

**Por que não imputaram `Peak CCU` == 0?** Zero ali significa ausência de telemetria, não "ninguém jogou". Imputar média ou mediana inventaria audiência. As perguntas P1 a P3 valem só para o subconjunto com pico real (cerca de 16%).

**Por que mantiveram outliers?** São valores reais (Counter-Strike 2 tem mais de 1 milhão de pico). Só se verifica o impossível (preço ou pico negativo, idade fora de 0 a 21).

**Por que mantiveram nomes repetidos?** A chave real é `AppID`, que é único. Repetição de `Name` vem de demos, remasters e edições.

**O que é `owners_avg`?** O ponto médio da faixa de `Estimated owners` (texto `"0 - 20000"` virou `owners_min`, `owners_max` e a média dos dois). É uma estimativa grosseira, não contagem.

**Por que pandas e não Spark no RA1?** ~125 mil linhas cabem em memória e processam em segundos numa máquina. Spark compensa em GB ou TB ou em processamento distribuído. No RA2 o Spark entra porque o tema é streaming.

**Que tipo de dado e de analytics?** Dado estruturado (CSV tabular). Analytics descritivo e diagnóstico; não há preditivo nem prescritivo.

**Quais são as perguntas do projeto?** P1 preço × `Peak CCU`; P2 gêneros e tags com maior pico; P3 nota de review e Metacritic × pico; P4 catálogo histórico × comportamento ao vivo.

## 3. Perguntas prováveis sobre o RA2

**Qual a diferença entre batch e streaming?** Batch processa um conjunto fechado de uma vez. Streaming trata os dados como uma tabela sem fim e atualiza o resultado conforme chegam registros novos.

**O que é micro-batch?** O Structured Streaming junta o que chegou desde a última execução e processa em pequenos lotes. Na demo, cada arquivo JSON que cai na pasta vira um micro-batch.

**Por que `readStream` com schema explícito?** Em streaming o Spark não pode ler o arquivo todo para inferir os tipos; o schema (`timestamp`, `appid`, `jogo`, `jogadores`) precisa estar definido de antemão.

**Por que escrever em `publicacao` e mover para `entrada`?** Para o Spark nunca ler um arquivo ainda sendo escrito. O `replace` é atômico: o arquivo só aparece na pasta monitorada já completo.

**Qual janela usaram e por quê?** Tumbling de 5 minutos, sem deslocamento: intervalos consecutivos, sem sobreposição, início incluído e fim excluído (a leitura das 14:05:00 entra na janela 14:05-14:10). Escolhemos tumbling porque cada leitura pertence a exatamente uma janela; fica fácil de ler e conferir.

**Qual a diferença para sliding?** Na sliding as janelas se sobrepõem (por exemplo, 5 min de duração com passo de 1 min), então uma leitura aparece em várias janelas. Suaviza a curva, mas repete dados.

**Qual agregação e o que cada janela calcula?** Média (`avg`) de `jogadores` por janela e por jogo: a média de jogadores simultâneos de cada jogo nas leituras daquele intervalo.

**O que faz `outputMode("complete")`?** Reescreve a tabela de resultado inteira a cada lote. Serve aqui porque há agregação e a tabela é pequena (9 linhas). `append` só emitiria janelas finalizadas e exigiria watermark; `update` emitiria só as linhas alteradas.

**Para que serve o `checkpointLocation`?** Guarda o progresso da consulta (quais arquivos já foram lidos) e o estado da agregação, para a consulta poder continuar de onde parou depois de uma falha ou reinício.

**Por que sink `memory` e `processAllAvailable()`?** `memory` guarda a tabela de resultado na memória do Spark, consultável com `spark.table(...)`, ótimo para demonstração (não para produção). `processAllAvailable()` bloqueia até processar tudo que já chegou, para a tabela mostrada refletir o lote.

**Por que só a janela em curso mudou?** Porque os novos registros pertencem a ela. As janelas fechadas não recebem leituras novas. O Spark mantém o estado da agregação e processa apenas os arquivos novos; o que é reescrito inteiro é a tabela de saída (modo `complete`).

**Por que a simulação é válida?** É o Cenário A do enunciado: dados estáticos, com chegada simulada de registros artificiais coerentes. Usamos os 3 jogos de maior `Peak CCU` do RA1 e nunca passamos do pico real.

**O que o `assert` final prova?** Que a média por janela calculada em streaming é idêntica à calculada em batch (pandas) sobre as mesmas 45 leituras: as 9 médias (3 janelas × 3 jogos) coincidem.

**Por que vocês geraram as leituras com semente fixa?** Reprodutibilidade: com `random.Random(42)` qualquer pessoa obtém os mesmos 45 valores e a mesma tabela.

## 4. Pontos fracos: admitir com honestidade

- **Dados simulados**: o streaming é exercício didático. Numa aplicação real, a fonte seria um coletor da Steam Web API ou do SteamSpy (Cenário B).
- **Sem watermark**: não tratamos dados atrasados. Hoje, se chegasse uma leitura atrasada para a janela 14:00, ela seria recalculada (sem watermark o Spark guarda o estado de todas as janelas). Em produção, definiríamos `withWatermark` para descartar atraso excessivo e limitar a memória.
- **Escala pequena**: 15 minutos, 3 jogos, 45 eventos. Mostra o conceito, não testa volume.
- **Ainda não respondemos P1 a P3**: o RA1 prepara os dados; a análise vem depois. P4 foi tocada de forma simplificada.
- **Cobertura**: `Peak CCU` existe em cerca de 16% do catálogo; Metacritic em 3,4%.
- **Dependência de ambiente**: o notebook precisa de Java 17 e do `games.csv`; o PDF é gerado por HTML + Chrome porque o TeX local não tem `tcolorbox`.

## 5. Demonstração em 5 minutos (sugestão de divisão)

Roteiro completo em [`roteiro_demo_RA2.md`](roteiro_demo_RA2.md). Divisão sugerida (ajustem entre vocês):
1. Problema e ligação com P4 (30 s) e fonte da simulação (45 s) — pessoa A.
2. Rodar os 3 lotes mostrando a janela 14:05-14:10 mudar de 832.067 para 859.085 no Counter-Strike 2 (2 min) — pessoa B, com A explicando.
3. Janela tumbling (1 min) e conferência streaming = batch, limites (45 s) — pessoa A.

Antes de entrar: kernel reiniciado, Java 17 funcionando, `Dataset/fronkongames/games.csv` no lugar. `Restart & Run All` leva cerca de 20 s; se algo falhar, mostrar o PDF com as saídas já geradas.
