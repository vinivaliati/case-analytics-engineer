# Arquitetura de dados: dashboard e agente sobre a mesma base

## Visão geral

```
contexto/dados/*.csv ──► staging ──► intermediate ──► core (Kimball) ──► analytics + serving ──► Parquet + data_dictionary.json
   (fonte, intocada)     (stg_*)       (int_*)        (dim_*, fct_*)      (mart_*, agg_*, dim_*)     (entrega/dashboard/data/)
                                                                              tag: published               ▲          ▲
                                                                                                 dashboard ┘          └ agente
```

Um comando reconstrói tudo: `python entrega/scripts/build.py` (confere SHA-256 → dbt build → export).

## Camadas e por quê

| Camada | Modelos | Grão | Materialização | Por quê |
|---|---|---|---|---|
| **staging** | `stg_<sistema>__<tabela>` (9) | o da origem | view | 1:1 com a fonte. Só tipagem, renomeação, fuso e dedup, com padrão fixo de 3 CTEs. A regra de negócio fica fora daqui. |
| **intermediate** | `int_*` (2) | declarado em cada modelo | view | Lógica reaproveitada por mais de um fato (ex.: ledger pivotado por conta × mês). |
| **core** | `dim_*` (6), `fct_*` (5) | atômico (item, movimento, evento) e snapshots | table | Star schema Kimball, com surrogate keys e membro desconhecido `-1`. É a fonte única da verdade e não é publicada (tem grão de cliente). |
| **analytics** | `mart_*` (6) | 1 pergunta da diretoria por mart | table | Cada mart responde uma pergunta e **trava o achado com testes** (ex.: Pix = R$ 0,019). |
| **serving** | `agg_*` (4), `dim_month`, `dim_card_class` | mensal agregado | table | Star schema **agregado** para dashboard, agente e BI. Sem dado linha a linha. |

Regras de negócio que mudam com o negócio ficam em **tabelas de referência** (`goal_categories`, `calendar_events`, `card_classes`), e não no SQL. Neste case elas são seeds dbt. Em produção seriam tabelas governadas no warehouse, mantidas pelo dono do negócio.

## Por que um star schema agregado na publicação (e não só marts prontos)

- **Dashboard:** os marts dão as respostas prontas, e os agregados permitem cortes livres (mês × produto × nível × canal).
- **BI futuro:** uma ferramenta como Power BI, Looker ou Metabase lê os Parquets e liga os fatos às dimensões pelas `*_key`, sem remodelar.
- **Agente:** consulta tabelas pequenas (no máximo 2,5 mil linhas) e com grão declarado, o que reduz o risco de somar errado.
- **Privacidade:** `dim_customer`, `dim_account` e os fatos atômicos não saem do banco. O build publicado tem 300 KB.

## Grão, nomes e métricas

- **O grão é declarado três vezes:** no comentário do SQL, na descrição do `schema.yml` e em `meta.grain`. O grão é testado com `unique` ou `unique_combination_of_columns`.
- **Convenção de nomes:**
  - `stg_` / `int_` / `dim_` / `fct_` / `agg_` / `mart_` indicam a camada;
  - os sufixos `_key` (surrogate), `_id` (natural), `_at` (timestamp local), `_brl` (R$), `_points`, `_pct` (0 a 100) e `is_`/`has_`/`meets_` (booleano) indicam o tipo.
- **Uma métrica oficial por conceito**, nomeada sem ambiguidade:
  - pontos resgatados = `net_redeemed_points` com `is_effective_redemption`;
  - metas = `goal_category_contract`;
  - breakage = `breakage_*_realized_pct`.
  - Métricas parecidas que **não** devem ser usadas como oficiais dizem isso na descrição (ex.: `expired_to_redeemed_pct`: "NÃO é breakage").
- **Aditividade explícita:** `closing_balance_points` é semi-aditivo (soma entre níveis, nunca entre meses). Contagens de clientes distintos não entram nos agregados, porque não são aditivas.
- **Nível de cartão:** é o nível atual do cliente, por decisão documentada. A alternativa é `dim_account.card_class`.

## Testes (242 no build)

- **Fonte:** contagem igual à do MANIFESTO, SHA-256 (no script) e pontos inteiros.
- **Estrutura:** PK única e não nula em todo modelo; FKs com `relationships`; domínios com `accepted_values`.
- **Reconciliação:**
  - pontos debitados = pontos pagos (item a item);
  - saldo do snapshot = soma do ledger (cliente a cliente);
  - agregados publicados = fatos de origem;
  - a visão contrato reproduz o relatório do operador com até 1,5 p.p.
- **Achados:** Pix = R$ 0,019 por ponto; o operador usa pontos de todos os status; nenhum ponto do programa novo expirou; nenhum cliente com saldo negativo.
- **Unitários:** fuso do CRM, dedup e tipagem.
- **Contrato de documentação:** o `build.py` falha se alguma coluna publicada estiver sem descrição.

## Como o agente descobre o que cada campo significa

1. O `build.py` gera `data_dictionary.json` a partir do `manifest.json` do dbt e do esquema real do DuckDB. Para cada tabela publicada, ele traz:
   - a descrição;
   - `meta.grain` e `meta.business_questions`, que dizem qual tabela responde qual pergunta;
   - `meta.caveat`, com as ressalvas que o agente deve repetir;
   - número de linhas e testes;
   - e, por coluna, tipo, descrição e testes.
2. **A documentação vive num lugar só** (`schema.yml`). O dashboard, o agente, o BI e o `dbt docs` leem a mesma fonte, e mudou no yml, mudou para todos.
3. O agente recebe o dicionário no prompt de sistema, gera SQL somente leitura sobre os Parquets (DuckDB) e cita a tabela usada. As ressalvas registradas em `caveat` e nas descrições ("descritivo, não causal", "hipótese") fazem parte da resposta.
