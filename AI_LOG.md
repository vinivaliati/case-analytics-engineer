# Registro de uso de IA

Uma entrada por sessão, da mais antiga para a mais recente. Formato e regras em `AGENTS.md`.


### 2026-10-25T13:30:33-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** ler o repositório do case e entender o desafio.
- **O que a IA fez ou sugeriu:** leu README, AGENTS.md, MANIFESTO e o guia da apresentação; fez um perfil exploratório dos CSVs em pandas (valores por coluna, faixas de datas, mix de pontos por categoria/mês, taxa R$/ponto do Pix nos itens). Nenhum código de entrega foi escrito.
- **O que o candidato conferiu, corrigiu ou rejeitou:** nada ainda (sessão só de leitura).
- **Arquivos criados ou alterados:** AI_LOG.md.

### 2026-10-25T13:39:14-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** criar a branch `entrega`, organizar os próximos passos e usar as skills "ponytail" e "superpowers"; não tomar decisões sem consultar o candidato.
- **O que a IA fez ou sugeriu:** criou a branch `entrega`; verificou que "superpowers" existe no marketplace mas não está instalado e que "ponytail" não foi encontrado; propôs um plano em 5 fases e perguntou as decisões de stack. Recomendou dbt + DuckDB e Next.js no Vercel.
- **O que o candidato conferiu, corrigiu ou rejeitou:** escolheu dbt, mas quer discutir antes se vale usar DuckDB; rejeitou a recomendação de Next.js e escolheu Streamlit; pediu o modo "proponho, você aprova, eu executo"; pediu só commit local, sem push.
- **Arquivos criados ou alterados:** AI_LOG.md.

### 2026-10-25T13:55:03-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** montar a camada de staging em dbt + DuckDB no padrão definido pelo candidato (CTE source, CTE de tipagem e renomeação, CTE de dedup, leading comma), com testes; modelagem Kimball; CRM em UTC; marts em Parquet como star schema; avaliar Airflow no fim.
- **O que a IA fez ou sugeriu:** criou o venv (dbt-core 1.12 + dbt-duckdb 1.11 no Python 3.14); perfilou chaves, nulos e formatos (nenhuma duplicata nas fontes; redeemed_points e crm_events sem chave natural, tratados com chave surrogate em hash de todas as colunas); confirmou nos dados que o CRM grava em UTC ('Order Approved' = orders.created_at + 3h em 17.385 de 17.494 eventos); criou 9 modelos stg, schema.yml com descrições e testes genéricos, testes de source (pontos inteiros), teste de contagem contra o MANIFESTO, teste de sinal do ledger vs direction e 4 testes unitários. Os unit tests falharam de início (sources externas sem metadados de coluna) e foram corrigidos com fixtures em SQL. Resultado: 76/76 PASS. Fez um teste de mutação (alterou o esperado de um unit test) para confirmar que o teste falha.
- **O que o candidato conferiu, corrigiu ou rejeitou:** definiu o padrão de staging, o uso de Kimball, a premissa de UTC e o star schema para BI futuro; a revisão dos modelos gerados ainda está pendente.
- **Arquivos criados ou alterados:** .gitignore, AI_LOG.md, dbt/dbt_project.yml, dbt/profiles.yml, dbt/packages.yml, dbt/macros/*.sql, dbt/models/staging/*.sql, dbt/models/staging/_sources.yml, dbt/models/staging/_stg_models.yml, dbt/tests/*.sql.

### 2026-10-25T14:06:20-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** sinalizar orders.user_id como ajuste de ingestão; construir os fatos e dimensões Kimball com PK/FK; usar o nível da conta que pagou (defender na apresentação); trazer mais contexto sobre a classificação das metas; commitar com bons nomes.
- **O que a IA fez ou sugeriu:** criou docs/notas_para_readme.md (ajustes de ingestão, decisões a defender, perguntas ao negócio, fatos confirmados) e meta ingestion_issue no schema.yml; construiu 6 dimensões, 4 fatos e 1 intermediate, seed de níveis de cartão e testes de reconciliação (pontos debitados = pagos; saldo do snapshot = ledger): 149/149 PASS. Corrigiu um erro próprio: coalesce sobre generate_surrogate_key nunca retornaria '-1' (o hash não é nulo), trocado por case when. Levantou o contexto das metas: o relatório do operador é reproduzido usando category_macro e itens aprovados (varejo inclui transferências a parceiros). Descobriu que 1.471 itens são pagos por várias contas (820 com níveis diferentes) e que o saldo funciona por cliente: 1.197 contas negativas, nenhum cliente negativo.
- **O que o candidato conferiu, corrigiu ou rejeitou:** a IA interpretou "order_id" como orders.user_id e "nível atual da conta" como o card_class da conta pagadora, e pediu confirmação; as decisões sobre as metas e o grão do snapshot estão pendentes com o candidato.
- **Arquivos criados ou alterados:** AI_LOG.md, docs/notas_para_readme.md, dbt/dbt_project.yml, dbt/seeds/*, dbt/models/intermediate/int_redeemed_points__per_item.sql, dbt/models/marts/core/*, dbt/tests/assert_pontos_debitados_batem_com_pagos.sql, dbt/tests/assert_saldo_final_bate_com_ledger.sql, dbt/models/staging/_stg_models.yml.

### 2026-10-25T14:11:57-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** aprovar recomendações (nível atual do cliente, snapshot cliente × mês, metas pela definição do operador + visão estrita), ver o plano dos próximos passos, reorganizar o repositório com tudo dentro de `entrega/` e começar a fazer push.
- **O que a IA fez ou sugeriu:** apresentou um plano em 6 etapas (aprovado); moveu dbt/ e docs/ para entrega/ (README.md, AI_LOG.md, dados/ e MANIFESTO ficam na raiz, como pede o contrato); ajustou os caminhos relativos das sources e o .gitignore; rodou de novo o dbt build (149/149 PASS); criou requirements.txt com versões fixas.
- **O que o candidato conferiu, corrigiu ou rejeitou:** aprovou o plano e pediu a reorganização antes de continuar.
- **Arquivos criados ou alterados:** entrega/dbt/** (movido), entrega/docs/** (movido), entrega/dbt/models/staging/_sources.yml, entrega/dbt/profiles.yml, .gitignore, requirements.txt, AI_LOG.md.

### 2026-10-25T14:14:45-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** mover os arquivos originais do case para outra pasta, para respeitar a estrutura de entrega.
- **O que a IA fez ou sugeriu:** moveu dados/, MANIFESTO_v1.csv e apresentacao-modelo/ para contexto/; deixou o caminho dos CSVs configurável por variável de ambiente (PONTUA_DADOS_DIR, padrão ../../contexto/dados). Primeira tentativa quebrou o YAML por aspas aninhadas, corrigida. Rodou o build de novo (149/149 PASS) e confirmou que a variável muda o caminho (apontando para uma pasta inexistente, o build falha). O README.md original continua na raiz até virar o README da entrega.
- **O que o candidato conferiu, corrigiu ou rejeitou:** sugeriu o nome "contexto".
- **Arquivos criados ou alterados:** contexto/** (movido), entrega/dbt/models/staging/_sources.yml, entrega/dbt/profiles.yml, AI_LOG.md.

### 2026-10-25T14:18:12-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** manter agente/ na raiz; executar a etapa 1 do plano (nível atual do cliente com justificativa documentada, snapshot cliente × mês, classificação das metas em seed).
- **O que a IA fez ou sugeriu:** documentou no schema.yml e nas notas o motivo de usar o nível atual do cliente (carteira por cliente; 820 itens com níveis mistos) e sua limitação; criou int_points_ledger__account_monthly, transformou o snapshot oficial em cliente × mês (teste: saldo nunca negativo e igual ao ledger) e manteve o snapshot por conta como detalhe; criou o seed goal_categories com as visões contract e strict e ligou à dim_product. 174/174 PASS. Conferiu que a visão contract reproduz o relatório do operador (≤ 0,3 p.p., exceto jun/2026 em aéreas: 56,3% vs 55%).
- **O que o candidato conferiu, corrigiu ou rejeitou:** aprovou as três recomendações da IA e pediu justificativa explícita na documentação.
- **Arquivos criados ou alterados:** entrega/dbt/seeds/goal_categories.csv, entrega/dbt/seeds/_seeds.yml, entrega/dbt/models/intermediate/*, entrega/dbt/models/marts/core/dim_product.sql, entrega/dbt/models/marts/core/fct_points_balance_monthly.sql, entrega/dbt/models/marts/core/fct_points_balance_account_monthly.sql, entrega/dbt/models/marts/core/_core_models.yml, entrega/dbt/tests/assert_saldo_*.sql, entrega/docs/notas_para_readme.md, AI_LOG.md.

### 2026-10-25T14:22:50-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** tratar goal_categories como em produção (tabela de referência no banco, não "editar CSV"); seguir para a etapa 2 (regras de negócio).
- **O que a IA fez ou sugeriu:** reescreveu a documentação de goal_categories como tabela de referência governada (seed só neste case); levantou evidências para as regras: estornos (207/220 casam com ESTORNO_PEDIDO; devolução parcial em 103 aprovados), validade (programa novo: 24 meses, nada expirou; migrado: expira ~7 mi/mês desde jan/2026 apesar de valid_until 2028) e o pico de 12/01/2026 (1.517 resgates aéreos, 75,9 mi pontos, distribuídos nas 24h, sem campanha de CRM associada). Registrou tudo nas notas e propôs regras para aprovação.
- **O que o candidato conferiu, corrigiu ou rejeitou:** corrigiu a forma de comunicar a regra das metas (pensar como produção).
- **Arquivos criados ou alterados:** entrega/dbt/seeds/_seeds.yml, entrega/dbt/models/marts/core/_core_models.yml, entrega/dbt/models/marts/core/dim_product.sql, entrega/docs/notas_para_readme.md, AI_LOG.md.

### 2026-10-25T14:29:05-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** aprovar a regra de resgate efetivo documentando o impacto para o negócio decidir; pesquisar benchmark de breakage com um case real; marcar 12/01/2026 como ponto importante da apresentação, com a hipótese de promoção a ser validada pelo negócio.
- **O que a IA fez ou sugeriu:** pesquisou na web e conferiu no texto do PDF do Relatório Anual 2012 da Multiplus (taxa de breakage 22,6%/24,1%/21,0% em 2010-2012; gestão da taxa numa faixa ideal; definição) e usou a Forbes Brasil (17,6% no 1T18). Um PDF veio ilegível pela ferramenta de fetch e foi extraído com pypdf; uma fonte (IFRS Community) bloqueou a leitura e foi marcada como tal. Criou docs/benchmark_breakage.md. Implementou is_effective_redemption e net_redeemed_points no fato, mediu o impacto (máx. 0,11 p.p.; nenhum mês muda de status de meta), criou a tabela de referência calendar_events e flags is_atypical_day e is_pre_pix_baseline na dim_date. 180/180 PASS.
- **O que o candidato conferiu, corrigiu ou rejeitou:** pediu embasamento externo para o breakage em vez de aceitar a definição proposta; direcionou a hipótese de 12/01 para a área de negócio.
- **Arquivos criados ou alterados:** entrega/docs/benchmark_breakage.md, entrega/docs/notas_para_readme.md, entrega/dbt/seeds/calendar_events.csv, entrega/dbt/seeds/_seeds.yml, entrega/dbt/dbt_project.yml, entrega/dbt/models/marts/core/dim_date.sql, entrega/dbt/models/marts/core/fct_redemption_items.sql, entrega/dbt/models/marts/core/_core_models.yml, AI_LOG.md.

### 2026-10-25T14:36:41-03:00 · Claude Code (VS Code) · Claude Opus 5.5
- **Pedido:** executar a etapa 3 (as três afirmações e a saúde financeira), com o preço do banco por ponto como hipótese declarada.
- **O que a IA fez ou sugeriu:** explorou os dados e criou 6 marts analíticos com testes que travam os achados: mart_goal_attainment_monthly, mart_pix_reconciliation_monthly, mart_points_flow_monthly, mart_crm_pix_launch_adoption, mart_crm_pix_launch_timing e mart_redemption_economics (202+ testes PASS). Achados: o Pix custa exatamente R$ 0,019/ponto; o operador divide R$ pagos por pontos de todos os status (bate exato); a adoção do Pix não difere entre quem recebeu ou não a comunicação; o breakage correto é 0% (programa novo) e 19,8% (migrado), e o "40%" provavelmente é expiração ÷ resgate; o Pix somou volume (aéreas e varejo cresceram em pontos absolutos) e é a modalidade mais cara por ponto. Escreveu entrega/docs/analise_afirmacoes.md.
- **O que o candidato conferiu, corrigiu ou rejeitou:** autorizou seguir com hipótese para o preço do banco. A IA corrigiu três erros próprios: testes expression_is_true em nível de coluna (sintaxe), contagem de destinatários do e-mail que incluía falhas de envio (9.600 → 9.284) e um número do documento (varejo estrito "nunca passou de 14%", na verdade 14,2%). Também moveu para um mart um número que estava só em consulta exploratória.
- **Arquivos criados ou alterados:** entrega/dbt/models/marts/analytics/*, entrega/dbt/tests/assert_adocao_crm_cobre_todos_os_clientes.sql, entrega/docs/analise_afirmacoes.md, AI_LOG.md.
