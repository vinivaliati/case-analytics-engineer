# Notas para o README final

Arquivo de trabalho: acumula o que deve entrar no README e na apresentação. Cada item traz a evidência.

## Ajustes de ingestão (sinalizar aos donos dos sistemas)

1. **`orders.user_id` vem 100% vazio** (19.785 de 19.785 linhas). O usuário do pedido é recuperado por `orders.cart_id → carts.user_id`; a cobertura é total (todo cart_id de orders existe em carts, testado com `relationships`). Pedido: corrigir a extração ou remover a coluna do contrato.
2. **`crm_events.event_ts` sem fuso.** Os demais sistemas gravam com offset `-03:00`; o CRM grava em UTC sem offset. Confirmado nos dados: o evento `Order Approved` acontece exatamente 3h depois de `orders.created_at` do mesmo usuário em 17.385 de 17.494 eventos. Pedido: exportar com offset explícito.
3. **`crm_events.control_group` 100% vazio.** Sem grupo de controle não é possível medir efeito causal das campanhas.
4. **`redeemed_points` sem chave natural.** `(order_item_id, movement_type)` se repete em 1.471 itens porque o pagamento foi dividido entre mais de uma conta do mesmo cliente. Pedido: expor um `movement_id` por linha.
5. **`crm_events` sem id de evento.** 2.179 eventos têm o mesmo instante, device, evento e campanha, diferindo só no payload. Pedido: expor um `event_id`.

## Decisões a defender na apresentação

1. **Nível do cartão = nível atual do cliente** (`dim_customer.current_card_class`, conta com `is_most_recent`).
   - Primeira proposta era o nível da conta que pagou o resgate. Foi trocada por dois achados nos dados:
     - **o saldo é uma carteira por cliente**: 1.197 contas fecham set/2026 negativas (−20,0 mi pontos), nenhum cliente fica negativo;
     - **820 itens são pagos por contas de níveis diferentes**, então "o nível da conta que pagou" não tem valor único.
   - Limitação: é o nível de hoje, não o da data do resgate. Um cliente que subiu de Gold para Black aparece como Black no histórico.
   - Alternativa disponível sem retrabalho: `dim_account.card_class` (por conta). Se o negócio preferir, é troca de join.
2. **Saldo de pontos no grão cliente × mês** (`fct_points_balance_monthly`). A versão por conta (`fct_points_balance_account_monthly`) fica como detalhe, com aviso de que contas podem ser negativas.
3. **Metas: visão oficial = definição do operador** (`goal_category_contract`, tabela de referência `goal_categories`).
   - Em produção, `goal_categories` seria uma tabela de referência governada no warehouse, mantida pelo dono do negócio com histórico de alterações; mudar a regra = atualizar a tabela e reprocessar. Neste case ela é um seed dbt porque não há sistema de origem para essa regra.
   - Evidência: com `category_macro` da origem e itens aprovados, reproduzimos o `aereas_pct` e `varejo_pct` do relatório com diferença ≤ 0,3 p.p. em todos os meses, exceto jun/2026 (aéreas 56,3% vs 55%), a investigar.
   - Visão de sensibilidade (`goal_category_strict`): varejo só com produto, sem transferências a parceiros e sem Decola Viagens. Nela o varejo já estava em 11 a 14% antes do Pix: a meta de 20% nunca teria sido cumprida.
   - Compra de pontos fica fora das duas visões (não é resgate).
4. **CRM tratado como UTC** e convertido para America/Sao_Paulo (evidência no item 2 de ingestão).

## Perguntas ao negócio

1. Transferências para programas parceiros (Nuvem Recompensas, Pontos Max) contam como varejo na meta? O operador as soma em varejo.
2. Decola Viagens (agência de viagens) está em `Varejo/PRODUTO`. É varejo mesmo, ou passagem vendida por agência?
3. `COMPRA_PONTOS` (cliente compra pontos com dinheiro) não debita pontos. Confirmar que fica fora das metas.
4. O que aconteceu em 12/01/2026? Carga de passagens do programa anterior, promoção não registrada no CRM ou reprocessamento?
5. Por que o saldo migrado expira ~7 mi pontos/mês desde jan/2026 se o `valid_until` dele é 31/03/2028? A regra de expiração do programa anterior foi mantida?
6. Qual a definição de breakage usada pela diretoria para o "40%"?

## Confirmado nos dados

- **Estornos.** Os itens ESTORNADO debitaram 3,13 mi pontos e foram devolvidos no ledger (ESTORNO_PEDIDO) em média 7 dias depois: 207 de 220 casam por conta e valor exato. A sobra de ESTORNO_PEDIDO (≈ 254 mil pontos) bate com o `refunded_points` de 103 itens APROVADO com devolução parcial (254.384 pontos).
- **Validade.** Crédito do programa novo vale 24 meses (101.593 de 101.593 movimentos); o primeiro vencimento é 25/09/2027. **Nenhum ponto do programa novo expirou até a extração.** Saldo migrado tem validade 31/03/2028, mas expira ~7 mi pontos/mês desde jan/2026 (EXPIRACAO_MIGRACAO), 64,1 mi no total (19,8% dos 324,0 mi migrados).
- **12/01/2026.** Um único dia concentra 1.517 resgates de aéreas e 75,9 mi pontos (86% de jan; um mês normal resgata ~16 a 19 mi no total). 1.687 dos 1.799 clientes de jan têm saldo migrado. Os resgates se distribuem igualmente nas 24h, inclusive de madrugada, e não há campanha de CRM relevante entre 05 e 12/01. Padrão de carga em lote, não de comportamento.

- Nenhuma fonte tem linhas duplicadas, nem pela chave nem pela linha inteira.
- No ledger, CREDIT tem sempre pontos > 0 e DEBIT sempre < 0 (teste `assert_sinal_do_ledger_bate_com_direcao`).
- Para itens APROVADO e ESTORNADO, a soma de `RESGATE` em `redeemed_points` = `order_items.paid_points` (17.823 itens). Itens CANCELADO, INVALIDO e AGUARDANDO_CONFIRMACAO não têm movimento de pontos.
- **O saldo de pontos é por cliente, não por conta.** Em set/2026, 1.197 contas têm saldo negativo (−20,0 mi pontos), mas somando as contas de cada cliente nenhum fica negativo. O resgate debita de uma conta do cliente usando saldo acumulado em outras.
- 1.471 itens são pagos por mais de uma conta; em 820 deles as contas têm níveis de cartão diferentes.
- Todo user_id e account_id do ledger, carrinhos, resgates e CRM existe em `cards`; o user_id do ledger bate com o dono da conta.
