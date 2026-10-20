# Roteiro da demonstração RA2 (5 minutos)

Notebook: `Notebooks/projeto_data_analytics.ipynb`. Antes de começar: abrir o notebook já executado e deixar o kernel pronto (`Kernel > Restart & Run All` leva cerca de 20 s).

1. **Problema (0:30)** — Steam, pergunta de pesquisa e ligação com a P4 (histórico x ao vivo). RA1 entregou `df_limpo` (125.855 × 42).
2. **Fonte da simulação (0:45)** — Cenário A: top 3 jogos por `Peak CCU` de `df_limpo` (Counter-Strike 2, Dota 2, PUBG). 45 leituras artificiais (1 por minuto por jogo, 15 min), sempre abaixo do pico real.
3. **Streaming ao vivo (2:00)** — rodar as três células de lote, uma por vez:
   - Lote 1: janela 14:00-14:05 completa; 14:05-14:10 só com 2 minutos.
   - Lote 2: a 14:05-14:10 **muda** (Counter-Strike 2: 832.067 para 859.085); abre a 14:10-14:15.
   - Lote 3: a 14:10-14:15 muda de novo (946.415 para 964.231). Janelas fechadas não mudam.
4. **Janela (1:00)** — tumbling, 5 min, média de `jogadores` por janela e por jogo; início incluído, fim excluído; cada leitura em uma só janela. Sliding sobreporia janelas.
5. **Conferência e limites (0:45)** — tabela comparativa (lotes 1, 2, 3) e `assert` streaming = batch. Simulação é exercício didático; em produção a fonte seria coletor da Steam Web API/SteamSpy.

Perguntas prováveis: por que tumbling? (cada leitura em um bloco, mais simples de ler); o que é `outputMode("complete")`? (tabela de resultado reescrita inteira a cada lote); para que serve o checkpoint? (guardar progresso e estado da consulta).
