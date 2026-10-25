-- Snapshot periódico. Grão: 1 linha por conta x mês, do primeiro mês com movimento até o mês da extração.
-- PK: points_balance_key. FKs: account_key, customer_key, month_date_key (1º dia do mês).
-- Base para saldo em aberto e breakage; a definição de breakage em si fica na camada de consumo.
with

movements as (
    select
        ledger.account_id
        , ledger.user_id
        , cast(date_trunc('month', ledger.movement_at) as date)     as month_start
        , operations.operation_name
        , ledger.points
    from {{ ref('stg_pontos__points_ledger') }} as ledger
    inner join {{ ref('stg_pontos__operations') }} as operations
        on ledger.operation_code = operations.operation_code
)

, monthly as (
    select
        account_id
        , user_id
        , month_start
        , sum(points) filter (where operation_name = 'CREDITO')                 as credited_points
        , sum(points) filter (where operation_name = 'CREDITO_MIGRACAO')        as migrated_points
        , -sum(points) filter (where operation_name = 'RESGATE')                as redeemed_points
        , sum(points) filter (where operation_name = 'ESTORNO_PEDIDO')          as order_refund_points
        , -sum(points) filter (where operation_name = 'ESTORNO_CREDITO')        as credit_reversal_points
        , -sum(points) filter (where operation_name = 'EXPIRACAO')              as expired_points
        , -sum(points) filter (where operation_name = 'EXPIRACAO_MIGRACAO')     as expired_migrated_points
        , sum(points)                                                           as net_change_points
    from movements
    group by account_id, user_id, month_start
)

, account_months as (
    select
        accounts.account_id
        , accounts.user_id
        , cast(months.month_start as date)                                      as month_start
    from (
        select account_id, any_value(user_id) as user_id, min(month_start) as first_month
        from monthly
        group by account_id
    ) as accounts
    inner join (
        select distinct month_start
        from {{ ref('dim_date') }}
        where date_day < cast('{{ var("extraction_date") }}' as date)
    ) as months
        on months.month_start >= accounts.first_month
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key(['account_months.account_id', 'account_months.month_start']) }}
                                                                                as points_balance_key
        , {{ dbt_utils.generate_surrogate_key(['account_months.account_id']) }} as account_key
        , {{ dbt_utils.generate_surrogate_key(['account_months.user_id']) }}    as customer_key
        , cast(strftime(account_months.month_start, '%Y%m%d') as integer)       as month_date_key
        , account_months.month_start
        , coalesce(monthly.credited_points, 0)                                  as credited_points
        , coalesce(monthly.migrated_points, 0)                                  as migrated_points
        , coalesce(monthly.redeemed_points, 0)                                  as redeemed_points
        , coalesce(monthly.order_refund_points, 0)                              as order_refund_points
        , coalesce(monthly.credit_reversal_points, 0)                           as credit_reversal_points
        , coalesce(monthly.expired_points, 0)                                   as expired_points
        , coalesce(monthly.expired_migrated_points, 0)                          as expired_migrated_points
        , coalesce(monthly.net_change_points, 0)                                as net_change_points
        , sum(coalesce(monthly.net_change_points, 0)) over (
            partition by account_months.account_id
            order by account_months.month_start
        )                                                                       as closing_balance_points
    from account_months
    left join monthly
        on account_months.account_id = monthly.account_id
        and account_months.month_start = monthly.month_start
)

select * from final
