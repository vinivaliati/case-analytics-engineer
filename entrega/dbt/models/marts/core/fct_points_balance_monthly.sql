-- Snapshot periódico de saldo. Grão: 1 linha por cliente x mês, do primeiro mês com movimento até o mês da extração.
-- PK: points_balance_key. FKs: customer_key, month_date_key.
-- O cliente é o grão da carteira: somando as contas, nenhum cliente fica com saldo negativo (testado).
with

monthly as (
    select
        user_id
        , month_start
        , sum(credited_points)              as credited_points
        , sum(migrated_points)              as migrated_points
        , sum(redeemed_points)              as redeemed_points
        , sum(order_refund_points)          as order_refund_points
        , sum(credit_reversal_points)       as credit_reversal_points
        , sum(expired_points)               as expired_points
        , sum(expired_migrated_points)      as expired_migrated_points
        , sum(net_change_points)            as net_change_points
    from {{ ref('int_points_ledger__account_monthly') }}
    group by user_id, month_start
)

, months as (
    select distinct month_start
    from {{ ref('dim_date') }}
    where date_day < cast('{{ var("extraction_date") }}' as date)
)

, customers as (
    select
        user_id
        , min(month_start)                  as first_month
    from monthly
    group by user_id
)

, customer_months as (
    select
        customers.user_id
        , months.month_start
    from customers
    inner join months
        on months.month_start >= customers.first_month
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key(['customer_months.user_id', 'customer_months.month_start']) }}
                                                                                as points_balance_key
        , {{ dbt_utils.generate_surrogate_key(['customer_months.user_id']) }}   as customer_key
        , cast(strftime(customer_months.month_start, '%Y%m%d') as integer)      as month_date_key
        , customer_months.month_start
        , coalesce(monthly.credited_points, 0)                                  as credited_points
        , coalesce(monthly.migrated_points, 0)                                  as migrated_points
        , coalesce(monthly.redeemed_points, 0)                                  as redeemed_points
        , coalesce(monthly.order_refund_points, 0)                              as order_refund_points
        , coalesce(monthly.credit_reversal_points, 0)                           as credit_reversal_points
        , coalesce(monthly.expired_points, 0)                                   as expired_points
        , coalesce(monthly.expired_migrated_points, 0)                          as expired_migrated_points
        , coalesce(monthly.net_change_points, 0)                                as net_change_points
        , sum(coalesce(monthly.net_change_points, 0)) over (
            partition by customer_months.user_id
            order by customer_months.month_start
        )                                                                       as closing_balance_points
    from customer_months
    left join monthly
        on customer_months.user_id = monthly.user_id
        and customer_months.month_start = monthly.month_start
)

select * from final
