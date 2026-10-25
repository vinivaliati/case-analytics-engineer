-- Itens APROVADO e ESTORNADO: pontos debitados em redeemed_points = paid_points de order_items.
-- Demais status (exceto COMPRA_PONTOS): nenhum ponto debitado.
select
    order_item_id
    , item_status
    , paid_points
    , points_debited
from {{ ref('fct_redemption_items') }}
inner join {{ ref('dim_product') }} using (product_key)
where not is_points_purchase
    and (
        (item_status in ('APROVADO', 'ESTORNADO') and points_debited <> paid_points)
        or (item_status not in ('APROVADO', 'ESTORNADO') and points_debited <> 0)
    )
