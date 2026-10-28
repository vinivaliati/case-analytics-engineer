# Case Analytics Engineer · Pontua+ (Brain003)

Entrega do exercício 1 (Programa Pontua+). O enunciado original está em [contexto/enunciado.md](contexto/enunciado.md).

**Resposta curta para a diretoria:** o Pix **somou volume** (de 18,9 para 31,0 mi pontos/mês) em vez de tirar resgates de aéreas e varejo. Ele derrubou os **percentuais** das metas: varejo está em 12,9%, abaixo da meta de 20% desde jun/2026, e aéreas em 59,1%, ainda acima de 50%. Além disso, o Pix é a modalidade mais cara (R$ 0,019/ponto). **As três afirmações não se sustentam.** A recomendação é coibir o Pix com calibragem (taxa e teto), renegociar o denominador das metas e corrigir o relatório do operador.

**Dashboard + agente no ar:** https://vinivaliati-case-analytics-engineer-entregadashboardapp-qytb2d.streamlit.app/

## Entregáveis

| Peça | Onde |
|---|---|
| **Dashboard publicado** (Streamlit Community Cloud, branch `entrega`) | https://vinivaliati-case-analytics-engineer-entregadashboardapp-qytb2d.streamlit.app/ |
| Apresentação para a diretoria | [entrega/apresentacao/index.html](entrega/apresentacao/index.html) (abrir no navegador; `?static` desliga animação para PDF) |
| Apresentação técnica | [entrega/apresentacao/tecnica.html](entrega/apresentacao/tecnica.html) |
| Código e testes (dbt + DuckDB) | [entrega/dbt/](entrega/dbt/) · build: [entrega/scripts/build.py](entrega/scripts/build.py) |
| Dashboard (Streamlit, 4 telas + agente) | [entrega/dashboard/](entrega/dashboard/) |
| Estrutura de dados para dashboard e agente | [entrega/docs/arquitetura_dados.md](entrega/docs/arquitetura_dados.md) |
| Agente analista (Gemini) | [agente/](agente/) · exemplos reais: [agente/exemplos.md](agente/exemplos.md) |
| Análise das afirmações | [entrega/docs/analise_afirmacoes.md](entrega/docs/analise_afirmacoes.md) |
| Benchmark de breakage (case Multiplus) | [entrega/docs/benchmark_breakage.md](entrega/docs/benchmark_breakage.md) |
| Registro de uso de IA | [AI_LOG.md](AI_LOG.md) |

## Como reconstruir e rodar

Pré-requisito: Python 3.12+ (testado em 3.14). Os CSVs ficam em `contexto/dados/`. Para usar outra pasta, defina `PONTUA_DADOS_DIR`.

```bash
python -m venv .venv && .venv/Scripts/activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python entrega/scripts/build.py                        # 1) confere SHA-256, roda dbt (210 testes), exporta Parquet + dicionário
python -m pytest agente/tests entrega/dashboard/tests  # 2) 19 testes do agente e do dashboard
python entrega/apresentacao/gerar_decks.py             # 3) regenera as apresentações a partir dos dados
streamlit run entrega/dashboard/app.py                 # 4) dashboard + agente
```

- **Nada é editado à mão.** O `build.py` falha se um CSV divergir do MANIFESTO, se um teste do dbt falhar ou se alguma coluna publicada estiver sem descrição.
- **Os números da apresentação** são lidos dos marts pelo `gerar_decks.py`.
- **Os Parquets agregados já estão versionados** em `entrega/dashboard/data/` (300 KB, sem dado linha a linha). O dashboard sobe em produção sem rodar o dbt.

### Agente: chave do Gemini

| Variável | Obrigatória | Uso |
|---|---|---|
| `GEMINI_API_KEY` | sim | chave da API do Gemini |
| `GEMINI_MODEL` | não | padrão `gemini-3.8-flash` |
| `GEMINI_FALLBACK_MODEL` | não | reservas separadas por vírgula, usadas em 429/503; padrão `gemini-3.6-flash,gemini-3.5-flash,gemini-3.5-flash-lite` |

- **Local:** copie [.env.example](.env.example) para `.env` (que está no `.gitignore`).
- **Produção (Streamlit Community Cloud):** aponte o app para `entrega/dashboard/app.py` e coloque as mesmas chaves em *Settings › Secrets*. A chave só é lida no servidor e nunca vai para o navegador.
- **Linha de comando:** `python -m agente "As metas foram cumpridas em setembro?"`.

> O enunciado cita Vercel como exemplo. Streamlit não roda no Vercel; a escolha foi o Streamlit (decisão do candidato) com deploy no Streamlit Community Cloud.

## Estrutura

```
contexto/            material original do case (dados, MANIFESTO, modelo de apresentação, enunciado)
entrega/
  dbt/               staging → intermediate → core (Kimball) → analytics + serving
  scripts/build.py   comando único de reconstrução
  dashboard/         Streamlit (app.py, views/, lib/, data/ = Parquets publicados, tests/)
  apresentacao/      index.html (diretoria), tecnica.html, gerar_decks.py
  docs/              arquitetura, análise, benchmark, notas
agente/              agente analista (ponto de entrada: agente.agent.ask / python -m agente)
```

## O que entendi dos dados

**Grão e chaves.** As chaves foram verificadas por testes `unique`, `not_null` e `relationships`.

| Arquivo | Grão | Chave | Relações e observações |
|---|---|---|---|
| `orders` | pedido | `order_id` | `cart_id` → carts. **`user_id` 100% vazio**: o usuário vem de `carts.user_id` |
| `order_items` | item de pedido | `order_item_id` | `order_id` → orders. `quantity` sempre 1. `paid_points` vazio só em `COMPRA_PONTOS` |
| `carts` | carrinho | `cart_id` | `user_id`, canal APP/WEB |
| `redeemed_points` | movimento de pontos por item | **sem chave natural** (surrogate = hash da linha) | 1.471 itens pagos por mais de uma conta; RESERVA + CANCELADO_RESERVA sempre se anulam |
| `points_ledger` | movimento de saldo | `movement_id` | `operation_code` → dim_operation; o sinal bate com CREDIT/DEBIT (testado) |
| `dim_operation` | tipo de operação | `operation_code` | 7 operações, inclusive as de migração |
| `cards` | conta de cartão | `account_id` | 12.000 clientes, 16.168 contas, exatamente 1 `is_most_recent` por cliente |
| `crm_events` | evento | **sem chave natural** (hash) | `event_ts` **em UTC** (os outros sistemas estão em -03:00); `control_group` 100% vazio |
| `relatorio_mensal_cliente` | mês | `mes` | números autodeclarados pelo operador, usados só para reconciliar |

**Datas.** Pedidos, ledger e cartões vêm com offset `-03:00`. O CRM vem sem offset e está em UTC: o evento `Order Approved` acontece exatamente 3h depois de `orders.created_at` em 17.385 de 17.494 eventos. Tudo foi convertido para America/Sao_Paulo.

**Dedup.** Nenhuma fonte tem duplicata, nem pela chave nem pela linha inteira. O dedup do staging fica como proteção.

### Confirmado nos dados

- **Resgate efetivo:** em itens APROVADO e ESTORNADO, o RESGATE de `redeemed_points` é igual a `paid_points` (17.823 itens). Os ESTORNADO são devolvidos no ledger cerca de 7 dias depois (207 de 220 casam). Há devolução parcial em 103 aprovados.
- **O saldo é uma carteira por cliente:** 1.197 contas fecham negativas em set/2026, mas nenhum cliente fica negativo.
- **Validade:** o crédito do programa novo vale 24 meses e **nada venceu até a extração**. O saldo migrado (324 mi pontos) expira cerca de 7 mi por mês desde jan/2026.
- **Metas:** a definição do operador (`category_macro`, com transferências e agência dentro de varejo) reproduz o relatório com até 1,5 p.p. de diferença.
- **Pix:** custa R$ 0,0190 por ponto em todos os meses. O operador divide os reais pagos pelos pontos de **todos** os status (bate exato).
- **CRM:** a adoção do Pix é igual entre quem recebeu e quem não recebeu comunicação. Só 6% dos que receberam o e-mail usaram o Pix na mesma semana.
- **12/01/2026:** 1.517 resgates aéreos e 75,9 mi pontos num único dia, distribuídos nas 24h, sem campanha no CRM.

### Hipóteses e decisões (revisáveis)

1. **Nível de cartão = nível atual do cliente.** O saldo é por cliente e 820 itens misturam níveis. A alternativa por conta está pronta em `dim_account`.
2. **Resgate efetivo = APROVADO, líquido de devoluções.** O impacto é de no máximo 0,11 p.p. e nenhum mês muda de status de meta.
3. **Metas pela definição do operador**, com a visão estrita e a visão sem Pix como sensibilidade. As regras ficam na tabela de referência `goal_categories`, que em produção seria uma tabela governada pelo negócio.
4. **Breakage = expirados ÷ emitidos, por safra e por origem** (IFRS 15; a Multiplus operou entre 21% e 24%).
5. **Custo por ponto ≈ valor do produto − dinheiro pago pelo cliente.** O preço que o banco paga não está nos dados.
6. **Linha de base antes do Pix = fev a 26/mai/2026.** Jan/2026 fica de fora por causa de 12/01. A causa de 12/01 é hipótese: promoção não registrada no CRM.
7. **CRM tratado como UTC.**

### Perguntas ao negócio e aos donos dos sistemas

1. O contrato conta o Pix no denominador das metas? Transferências a parceiros e a Decola Viagens contam como varejo?
2. Quanto o banco paga por ponto, e em que momento (emissão ou resgate)? Qual o custo real dos parceiros de varejo do grupo?
3. O que aconteceu em 12/01/2026?
4. Por que o saldo migrado expira desde jan/2026 se o `valid_until` dele é 31/03/2028?
5. Qual definição de breakage gerou o "40%"?
6. **Operador:** qual a regra do R$ do Pix? Ele fica 0,2% a 0,7% abaixo do pago.
7. **Ingestão:**
   - `orders.user_id` vem vazio;
   - o CRM vem sem offset e sem `event_id`;
   - `redeemed_points` vem sem `movement_id`;
   - `control_group` vem vazio.

   Detalhes em [entrega/docs/notas_para_readme.md](entrega/docs/notas_para_readme.md).

**Dúvidas e esclarecimentos recebidos do recrutador:** nenhum.

## Orquestração: vale usar Airflow?

**Avaliação: não agora; sim quando houver ingestão recorrente.**
- **Hoje:** os dados são uma extração única e o `build.py` é idempotente e roda em menos de 1 minuto. Airflow acrescentaria infraestrutura (scheduler, banco de metadados, workers) sem ganho para o avaliador.
- **Em produção, com cargas diárias:** a DAG seria simples, porque o `build.py` já está separado em etapas:

  `sensor de chegada dos arquivos → conferir manifesto/SHA → dbt source freshness → dbt build (seeds, run, test) → exportar Parquet + dicionário → publicar dashboard → alerta em falha`

  Com `dbt build` falhando em qualquer teste, a publicação não acontece.
- **Alternativas mais leves para o mesmo papel:** Dagster (assets que mapeiam 1:1 os modelos dbt) ou um agendamento de CI (GitHub Actions) rodando o `build.py`.

## Tempo gasto

Cerca de **2h30** de trabalho, em 25/10/2026, das 13h30 às ~16h00, conforme os registros com horário em [AI_LOG.md](AI_LOG.md) e os commits.

## Uso de IA

Tudo foi feito com **Claude Code (Claude Opus 5.5)** no VS Code, com o candidato aprovando cada decisão de estrutura e de regra de negócio antes da execução. O registro por sessão está em [AI_LOG.md](AI_LOG.md).

**O que o candidato decidiu ou corrigiu:**
- dbt + DuckDB, modelagem Kimball, o padrão das CTEs no staging e Streamlit;
- a estrutura `entrega/` + `contexto/`;
- o dashboard em 4 telas, com o agente na visão geral;
- tratar regras de negócio como tabela de referência ("em produção não falamos em editar CSV");
- pedir benchmark externo para o breakage;
- o ajuste de layout dos big numbers.

**O que a IA errou e foi corrigido** (com teste ou screenshot):
- contagem de destinatários do CRM que incluía falhas de envio;
- `coalesce` sobre hash que nunca retornava `-1`;
- SHA-256 quebrado pelo `autocrlf` do Git;
- números escritos à mão no dashboard;
- cor de modalidade usada em séries que não eram modalidade;
- arredondamento diferente entre o dashboard e o deck;
- waterfall com soma em ponto flutuante;
- o agente travando sob 503/429 do Gemini.

**Skills usadas:** `dataviz` (paleta e regras dos gráficos). O validador de paleta não rodou porque o Node não está instalado; foram usados os valores já validados da paleta de referência. **Pesquisa web:** benchmark de breakage (Multiplus, conferido no PDF do relatório anual) e SDK e modelos do Gemini.

## Como seguiria

- Validar as hipóteses com o negócio, em especial o preço por ponto e o denominador das metas, e reprocessar.
- Breakage projetado por safra para o programa novo.
- Teste A/B da nova taxa do Pix com grupo de controle.
- Testes de regressão do agente com um conjunto fixo de perguntas e respostas esperadas.
