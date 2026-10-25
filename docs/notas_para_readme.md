# Notas para o README final

Arquivo de trabalho: acumula o que deve entrar no README e na apresentação. Cada item traz a evidência.

## Ajustes de ingestão (sinalizar aos donos dos sistemas)

1. **`orders.user_id` vem 100% vazio** (19.785 de 19.785 linhas). O usuário do pedido é recuperado por `orders.cart_id → carts.user_id`; a cobertura é total (todo cart_id de orders existe em carts, testado com `relationships`). Pedido: corrigir a extração ou remover a coluna do contrato.
2. **`crm_events.event_ts` sem fuso.** Os demais sistemas gravam com offset `-03:00`; o CRM grava em UTC sem offset. Confirmado nos dados: o evento `Order Approved` acontece exatamente 3h depois de `orders.created_at` do mesmo usuário em 17.385 de 17.494 eventos. Pedido: exportar com offset explícito.
3. **`crm_events.control_group` 100% vazio.** Sem grupo de controle não é possível medir efeito causal das campanhas.
4. **`redeemed_points` sem chave natural.** `(order_item_id, movement_type)` se repete em 1.471 itens porque o pagamento foi dividido entre mais de uma conta do mesmo cliente. Pedido: expor um `movement_id` por linha.
5. **`crm_events` sem id de evento.** 2.179 eventos têm o mesmo instante, device, evento e campanha, diferindo só no payload. Pedido: expor um `event_id`.

## Decisões a defender na apresentação

1. **Nível do cartão = nível da conta que pagou o resgate**, e não o nível atual do cliente.
   - Por quê: o resgate debita pontos de uma conta específica (`redeemed_points.account_id`). Cada conta tem um único nível, e a conta é quem gera e gasta os pontos. O nível atual do cliente (`is_most_recent`) mudaria a história retroativamente quando ele troca de cartão.
   - Ponto aberto: 820 itens são pagos por contas de dois níveis diferentes (ver decisões pendentes).
   - Se o negócio preferir o nível atual do cliente, a troca é só de join: `dim_customer.current_card_class`.
2. **CRM tratado como UTC** e convertido para America/Sao_Paulo (evidência no item 2 de ingestão).

## Perguntas ao negócio

1. Transferências para programas parceiros (Nuvem Recompensas, Pontos Max) contam como varejo na meta? O operador as soma em varejo.
2. Decola Viagens (agência de viagens) está em `Varejo/PRODUTO`. É varejo mesmo, ou passagem vendida por agência?
3. `COMPRA_PONTOS` (cliente compra pontos com dinheiro) não debita pontos. Confirmar que fica fora das metas.

## Confirmado nos dados

- Nenhuma fonte tem linhas duplicadas, nem pela chave nem pela linha inteira.
- No ledger, CREDIT tem sempre pontos > 0 e DEBIT sempre < 0 (teste `assert_sinal_do_ledger_bate_com_direcao`).
- Para itens APROVADO e ESTORNADO, a soma de `RESGATE` em `redeemed_points` = `order_items.paid_points` (17.823 itens). Itens CANCELADO, INVALIDO e AGUARDANDO_CONFIRMACAO não têm movimento de pontos.
- Todo user_id e account_id do ledger, carrinhos, resgates e CRM existe em `cards`; o user_id do ledger bate com o dono da conta.
