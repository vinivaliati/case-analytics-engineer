-- Grão: 1 linha por conta x mês com pelo menos um movimento no ledger.
-- Pivota os movimentos por tipo de operação. Débitos aparecem em módulo (positivos).
with

ledger as (
    select * from {{ ref('stg_pontos__points_ledger') }}
)

, operations as (
    select * from {{ ref('stg_pontos__operations') }}
)

, movements as (
    select
        ledger.account_id
        , ledger.user_id
        , cast(date_trunc('month', ledger.movement_at) as date)     as month_start
        , operations.operation_name
        , ledger.points
    from ledger
    inner join operations
        on ledger.operation_code = operations.operation_code
)

, monthly as (
    select
        account_id
        , user_id
        , month_start
        , coalesce(sum(points) filter (where operation_name = 'CREDITO'), 0)               as credited_points
        , coalesce(sum(points) filter (where operation_name = 'CREDITO_MIGRACAO'), 0)      as migrated_points
        , coalesce(-sum(points) filter (where operation_name = 'RESGATE'), 0)              as redeemed_points
        , coalesce(sum(points) filter (where operation_name = 'ESTORNO_PEDIDO'), 0)        as order_refund_points
        , coalesce(-sum(points) filter (where operation_name = 'ESTORNO_CREDITO'), 0)      as credit_reversal_points
        , coalesce(-sum(points) filter (where operation_name = 'EXPIRACAO'), 0)            as expired_points
        , coalesce(-sum(points) filter (where operation_name = 'EXPIRACAO_MIGRACAO'), 0)   as expired_migrated_points
        , sum(points)                                                                      as net_change_points
    from movements
    group by account_id, user_id, month_start
)

select * from monthly
