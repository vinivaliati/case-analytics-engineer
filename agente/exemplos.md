# Agente analista: exemplos reais

Perguntas feitas ao agente em 25/10/2026 com o Gemini (plano gratuito), via `python -m agente`. As respostas abaixo são a saída
do modelo sem edição. O campo "Modelo" mostra quem respondeu: a cota gratuita do `gemini-3.8-flash` (20 requisições/dia)
acabou durante os testes e o agente usou os modelos de reserva, como projetado.

Cada resposta foi conferida contra os marts do dbt (linha "Conferência").

## 1. As metas de aéreas e varejo foram cumpridas em setembro de 2026?

- **Modelo:** `gemini-3.5-flash` · **tempo:** 58.9 s · **consultas SQL:** 2
- **Conferência:** Conferido contra `mart_goal_attainment_monthly` (set/2026): 59,09% / 12,85% / 28,06%; sem Pix 82,13% / 17,87%. Esta resposta usou notação LaTeX (`$\ge 50\%$`); depois dela o prompt passou a proibir LaTeX.

<details><summary>SQL executado</summary>

```sql
SELECT 
    month_start,
    redeemed_points,
    aereas_points,
    aereas_pct,
    meets_aereas_goal,
    varejo_points,
    varejo_pct,
    meets_varejo_goal,
    pix_points,
    pix_pct
FROM mart_goal_attainment_monthly
WHERE month_start = '2026-09-01'
```

</details>

<details><summary>SQL executado</summary>

```sql
SELECT 
    month_start,
    aereas_pct_ex_pix,
    varejo_pct_ex_pix,
    operator_aereas_pct,
    operator_varejo_pct
FROM mart_goal_attainment_monthly
WHERE month_start = '2026-09-01'
```

</details>

**Resposta:**

Em setembro de 2026, **apenas a meta contratual de aéreas foi cumprida**. A meta de varejo **não foi atingida**.

### Desempenho em Setembro/2026:

* **Aéreas (Meta: $\ge 50\%$): CUMPRIDA**
  * **Participação:** **59,09%** dos pontos resgatados (19.762.300 pontos).
* **Varejo (Meta: $\ge 20\%$): NÃO CUMPRIDA**
  * **Participação:** **12,85%** dos pontos resgatados (4.298.540 pontos).

---

### Contexto Relevante
* **Total de pontos resgatados no mês:** 33.446.506 pontos.
* **Impacto do Pix:** O resgate em Pix representou **28,06%** (9.385.666 pontos) do volume total no mês, ampliando a base de cálculo e diluindo a participação percentual das demais categorias.
* **Cenário sem Pix (sensibilidade):** Caso o Pix fosse excluído do denominador das metas contratuais, a participação de Aéreas seria de **82,13%** e a de Varejo de **17,87%** (permanecendo abaixo da meta contratual de 20%).

*(Fonte: `mart_goal_attainment_monthly`)*

## 2. Quanto o Pix custa por ponto? O relatório do operador diz R$ 0,016, está certo?

- **Modelo:** `gemini-3.5-flash` · **tempo:** 32.0 s · **consultas SQL:** 2
- **Conferência:** Conferido contra `mart_pix_reconciliation_monthly`: R$ 0,0190 em todos os meses; 6.566.853 pontos não pagos somados pelo operador.

<details><summary>SQL executado</summary>

```sql
SELECT 
    month_start,
    effective_transactions,
    effective_points,
    effective_brl,
    effective_brl_per_point,
    all_status_points,
    operator_points,
    operator_brl,
    operator_brl_per_point,
    operator_points_match_all_status
FROM mart_pix_reconciliation_monthly
ORDER BY month_start
```

</details>

<details><summary>SQL executado</summary>

```sql
SELECT 
    SUM(effective_points) AS total_effective_points,
    SUM(effective_brl) AS total_effective_brl,
    SUM(effective_brl) / SUM(effective_points) AS avg_effective_brl_per_point,
    SUM(operator_points) AS total_operator_points,
    SUM(operator_brl) AS total_operator_brl,
    SUM(operator_brl) / SUM(operator_points) AS avg_operator_brl_per_point,
    SUM(all_status_points) AS total_all_status_points
FROM mart_pix_reconciliation_monthly
```

</details>

**Resposta:**

O custo real do Pix é de **R$ 0,019 por ponto** (ou 1,9 centavo por ponto). 

O número de **R$ 0,016 por ponto** apresentado pelo operador **não está correto** para medir o custo do programa. Esse valor distorcido ocorre porque o operador divide os valores financeiros pagos pelo volume de pontos de **todos os status** (incluindo tentativas canceladas, inválidas, estornadas ou pendentes), e não apenas pelos resgates efetivamente concluídos. *(fonte: mart_pix_reconciliation_monthly)*

---

### Resumo dos Dados Acumulados (Mai/2026 a Set/2026)

* **Resgates Efetivos (Visão Correta - Aprovados):**
  * **Pontos resgatados:** 37.979.434 pontos
  * **Valor creditado aos clientes:** R$ 721.610,73
  * **Custo efetivo por ponto:** **R$ 0,0190** (constante em todos os meses)

* **Relatório do Operador (Visão Distorcida - Todos os Status):**
  * **Pontos computados pelo operador:** 44.546.287 pontos (inclui 6.566.853 pontos de transações não efetivadas)
  * **Valor financeiro no relatório:** R$ 718.370,80
  * **Custo por ponto mostrado:** **R$ 0,0161**

---

### Evolução Mensal

| Mês | Pontos Efetivos | R$ Efetivo | Custo Real (R$/ponto) | Pontos Relatório Operador | Custo Operador (R$/ponto) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Mai/2026** | 1.051.095 | R$ 19.970,83 | **R$ 0,019** | 1.202.701 | R$ 0,0166 |
| **Jun/2026** | 9.215.135 | R$ 175.087,95 | **R$ 0,019** | 10.709.419 | R$ 0,0163 |
| **Jul/2026** | 8.960.664 | R$ 170.253,03 | **R$ 0,019** | 10.445.204 | R$ 0,0163 |
| **Ago/2026** | 9.366.874 | R$ 177.970,87 | **R$ 0,019** | 10.672.206 | R$ 0,0166 |
| **Set/2026** | 9.385.666 | R$ 178.328,05 | **R$ 0,019** | 11.516.757 | R$ 0,0154 |

## 3. Nosso breakage está em 40%?

- **Modelo:** `gemini-3.5-flash` · **tempo:** 8.1 s · **consultas SQL:** 1
- **Conferência:** Conferido contra `mart_points_flow_monthly`: 0% (novo), 19,78% (migrado); 43,8% / 37,7% / 36,2% em fev-abr.

<details><summary>SQL executado</summary>

```sql
SELECT 
    month_start,
    breakage_new_program_realized_pct,
    breakage_migrated_realized_pct,
    expired_to_redeemed_pct,
    total_expired_points,
    redeemed_points,
    credited_points,
    migrated_points
FROM mart_points_flow_monthly
ORDER BY month_start DESC
```

</details>

**Resposta:**

**Não, o breakage do programa não está em 40%.**

*(Fonte: `mart_points_flow_monthly`)*

### Breakage Real (acumulado até set/2026)
* **Programa Novo:** **0%**. Os pontos gerados no programa novo têm validade de 24 meses e o primeiro vencimento ocorrerá apenas em 25/09/2027.
* **Saldo Migrado:** **19,8%** (19,78%). Corresponde ao percentual acumulado de pontos migrados do programa anterior que já expiraram em relação ao total de saldo migrado.

---

### Origem da confusão dos 40%
O número de ~40% deriva de uma métrica incorreta: a relação **Pontos Expirados / Pontos Resgatados no Mês** (`expired_to_redeemed_pct`), que **não é breakage**. 

Nos primeiros meses de 2026, com o acúmulo de expirações do saldo migrado antigo combinado com um volume menor de resgates, essa razão atingiu picos pontuais:
* **Fevereiro/2026:** 43,8%
* **Março/2026:** 37,7%
* **Abril/2026:** 36,2%

Com o aumento dos resgates (especialmente após o lançamento do Pix em maio/2026), essa relação caiu para **20,7%** em setembro/2026.

## 4. A comunicação de lançamento explica o sucesso do Pix?

- **Modelo:** `gemini-3.6-flash` · **tempo:** 22.4 s · **consultas SQL:** 2
- **Conferência:** Responde com ressalva (sem grupo de controle), como esperado. Números iguais a `mart_crm_pix_launch_adoption` e `mart_crm_pix_launch_timing`.

<details><summary>SQL executado</summary>

```sql
SELECT exposure_segment, had_prior_redemption, customers, pix_adopters, pix_adoption_pct FROM mart_crm_pix_launch_adoption ORDER BY had_prior_redemption, exposure_segment
```

</details>

<details><summary>SQL executado</summary>

```sql
SELECT timing_window, customers, customers_pct FROM mart_crm_pix_launch_timing ORDER BY timing_window
```

</details>

**Resposta:**

**Não é possível afirmar que a comunicação explica a adoção do Pix.** A análise de CRM é estritamente descritiva e **não permite inferir efeito causal**, pois não houve grupo de controle reservado durante a campanha (fonte: `mart_crm_pix_launch_adoption`).

Além disso, a leitura descritiva dos dados aponta que a taxa de adoção do Pix varia pouco com a comunicação e está muito mais correlacionada ao histórico de engajamento prévio do cliente no programa.

---

### 1. Comparativo de Adoção do Pix por Exposição à Comunicação
*(Fonte: `mart_crm_pix_launch_adoption`)*

* **Clientes com resgate prévio no programa:**
  * **Recebeu e clicou no e-mail de lançamento:** 26,32% de adoção (20 de 76 clientes)
  * **Recebeu o e-mail, mas não clicou:** 24,15% de adoção (706 de 2.924 clientes)
  * **Não recebeu o e-mail do Pix (recebeu outra campanha):** 26,49% de adoção (142 de 536 clientes)
  * **Nenhuma comunicação na janela:** 22,71% de adoção (77 de 339 clientes)

* **Clientes sem resgate prévio no programa:**
  * **Recebeu e clicou no e-mail de lançamento:** 10,80% de adoção (19 de 176 clientes)
  * **Recebeu o e-mail, mas não clicou:** 14,91% de adoção (911 de 6.108 clientes)
  * **Não recebeu o e-mail do Pix (recebeu outra campanha):** 13,53% de adoção (157 de 1.160 clientes)
  * **Nenhuma comunicação na janela:** 15,86% de adoção (108 de 681 clientes)

---

### 2. Tempo até o Primeiro Resgate Pix
*(Fonte: `mart_crm_pix_launch_timing`)*

Entre os clientes que receberam o e-mail de lançamento e realizaram ao menos um Pix:
* **71,26% (1.180 clientes)** só fizeram o primeiro Pix **mais de 30 dias** após o e-mail.
* **21,98% (364 clientes)** fizeram entre 8 e 30 dias.
* **6,04% (100 clientes)** fizeram em **até 7 dias**.
* **0,72% (12 clientes)** realizaram o Pix antes do envio da mensagem.

---

### Ressalvas e Conclusão
* **Ausência de grupo de controle:** O campo de controle esteve 100% vazio no lançamento, impedindo medir o incremento real trazido pela régua de e-mail.
* **Fator determinante:** O histórico de uso do programa tem relação muito mais forte com a adoção do que o impacto direto da mensagem (clientes já ativos resgatam Pix a uma taxa de ~23% a 26%, enquanto novos/inativos resgatam a ~11% a 16%).
* **Hipótese x Dado confirmado:** A ideia de que o e-mail impulsionou o lançamento permanece como uma hipótese não comprovada pelos dados disponíveis. Recomendamos desenhar os próximos lançamentos de CRM com grupos de controle (holdout) para isolar o ganho incremental de comunicação.

## 5. Qual foi o percentual de varejo por nível de cartão em agosto de 2026?

- **Modelo:** `gemini-3.5-flash-lite` · **tempo:** 12.3 s · **consultas SQL:** 3
- **Conferência:** Conferido recalculando no `agg_redemptions_monthly`: os 6 percentuais da visão contrato batem exatamente.

<details><summary>SQL executado</summary>

```sql
SELECT 
    cc.card_class,
    cc.card_class_rank,
    SUM(r.net_redeemed_points) AS total_points,
    SUM(CASE WHEN p.goal_category_contract = 'varejo' THEN r.net_redeemed_points ELSE 0 END) AS varejo_contract_points,
    SUM(CASE WHEN p.goal_category_strict = 'varejo' THEN r.net_redeemed_points ELSE 0 END) AS varejo_strict_points,
    ROUND(100.0 * SUM(CASE WHEN p.goal_category_contract = 'varejo' THEN r.net_redeemed_points ELSE 0 END) / NULLIF(SUM(r.net_redeemed_points), 0), 2) AS varejo_contract_pct,
    ROUND(100.0 * SUM(CASE WHEN p.goal_category_strict = 'varejo' THEN r.net_redeemed_points ELSE 0 END) / NULLIF(SUM(r.net_redeemed_points), 0), 2) AS varejo_strict_pct
FROM agg_redemptions_monthly r
JOIN dim_month m ON r.month_date_key = m.month_date_key
JOIN dim_product p ON r.product_key = p.product_key
JOIN dim_card_class cc ON r.card_class_key = cc.card_class_key
WHERE m.year_month = '2026-08'
  AND r.is_effective_redemption = TRUE
GROUP BY cc.card_class, cc.card_class_rank
ORDER BY cc.card_class_rank
```

</details>

<details><summary>SQL executado</summary>

```sql
SELECT 
    cc.card_class,
    r.is_effective_redemption,
    SUM(r.net_redeemed_points) AS net_points
FROM agg_redemptions_monthly r
JOIN dim_month m ON r.month_date_key = m.month_date_key
JOIN dim_card_class cc ON r.card_class_key = cc.card_class_key
WHERE m.year_month = '2026-08'
GROUP BY cc.card_class, r.is_effective_redemption
ORDER BY cc.card_class
```

</details>

<details><summary>SQL executado</summary>

```sql
SELECT 
    month_start,
    redeemed_points,
    varejo_points,
    varejo_pct,
    varejo_strict_pct
FROM mart_goal_attainment_monthly
WHERE month_start = '2026-08-01'
```

</details>

**Resposta:**

Em agosto de 2026, o percentual de resgates de varejo por nível de cartão (com base nos resgates efetivos, líquidos de devoluções, da tabela `agg_redemptions_monthly`) foi o seguinte:

* **Essencial:** 12,07% (Visão Contrato) / 6,57% (Visão Estrita)
* **Gold:** 12,84% (Visão Contrato) / 9,06% (Visão Estrita)
* **Platinum:** 11,40% (Visão Contrato) / 6,54% (Visão Estrita)
* **Platinum Elo:** 12,80% (Visão Contrato) / 7,73% (Visão Estrita)
* **Infinite:** 12,31% (Visão Contrato) / 7,93% (Visão Estrita)
* **Black:** 11,37% (Visão Contrato) / 6,45% (Visão Estrita)

**Ressalvas e definições:**
* **Nível de cartão:** Refere-se ao nível atual do cliente.
* **Visão Contrato:** Categoria oficial de metas do operador (inclui produtos de varejo, transferências a parceiros e agência de viagens).
* **Visão Estrita:** Critério de sensibilidade que considera apenas produtos de varejo tradicionais (sem transferências e sem agência de viagens).

## 6. Quais clientes mais resgataram via Pix? Quero a lista com os IDs.

- **Modelo:** `gemini-3.5-flash-lite` · **tempo:** 2.3 s · **consultas SQL:** 1
- **Conferência:** **Recusa esperada**: pede dado individual, que não é publicado (privacidade).

<details><summary>SQL executado</summary>

```sql
SELECT table_name, column_name FROM information_schema.columns WHERE column_name LIKE '%customer%' OR column_name LIKE '%id%'
```

</details>

**Resposta:**

Como os dados publicados do Pontua+ são agregados por motivos de privacidade, **não é possível fornecer listas de clientes, contas ou IDs específicos**. As tabelas disponíveis contêm apenas métricas agregadas (como volume de pontos, contagens de clientes e valores financeiros).

Se precisar saber o volume total de resgates via Pix, a participação nos pontos resgatados ou a evolução por período, posso consultar esses dados agregados para você.

## 7. Quanto o banco paga por ponto ao programa?

- **Modelo:** `gemini-3.5-flash-lite` · **tempo:** 1.3 s · **consultas SQL:** 0
- **Conferência:** **Ressalva esperada**: o dado não existe na base; o agente diz o que seria preciso.

**Resposta:**

Essa informação **não está disponível nos dados** publicados do programa Pontua+. 

De acordo com o dicionário de dados (especificamente na tabela `mart_redemption_economics`), o preço real pago pelo banco por ponto não consta nas bases, e o custo por ponto de outras modalidades (como aéreas e varejo) é estimado por meio do valor do produto líquido do dinheiro pago pelo cliente.

Para responder a essa pergunta, seria necessário acessar os contratos comerciais firmados entre o Banco Aurora e o operador do programa Pontua+.

