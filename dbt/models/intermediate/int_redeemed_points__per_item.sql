-- Grão: 1 linha por item de pedido com movimento de pontos.
-- Resume redeemed_points: pontos debitados (RESGATE), contas envolvidas e saldo líquido das reservas.
with

redeemed as (
    select * from {{ ref('stg_pedidos__redeemed_points') }}
)

, per_item as (
    select
        order_item_id
        , -sum(points) filter (where movement_type = 'RESGATE')                         as points_debited
        , count(distinct account_id) filter (where movement_type = 'RESGATE')           as paying_accounts_count
        , coalesce(sum(points) filter (
            where movement_type in ('RESERVA', 'CANCELADO_RESERVA')), 0)                as reservation_net_points
    from redeemed
    group by order_item_id
)

select * from per_item
