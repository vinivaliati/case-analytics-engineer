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
