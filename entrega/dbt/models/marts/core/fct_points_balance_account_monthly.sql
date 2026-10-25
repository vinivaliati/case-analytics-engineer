-- Snapshot periódico (detalhe). Grão: 1 linha por conta x mês, do primeiro mês com movimento até o mês da extração.
-- PK: points_balance_account_key. FKs: account_key, customer_key, month_date_key.
-- ATENÇÃO: o saldo existe por cliente, não por conta. Contas podem ficar negativas porque o resgate
-- debita de uma conta usando saldo de outras do mesmo cliente. Para saldo use fct_points_balance_monthly.
with

monthly as (
    select * from {{ ref('int_points_ledger__account_monthly') }}
)

, months as (
    select distinct month_start
    from {{ ref('dim_date') }}
    where date_day < cast('{{ var("extraction_date") }}' as date)
)

, accounts as (
    select
        account_id
        , any_value(user_id)                as user_id
        , min(month_start)                  as first_month
    from monthly
    group by account_id
)

, account_months as (
    select
        accounts.account_id
        , accounts.user_id
        , months.month_start
    from accounts
    inner join months
        on months.month_start >= accounts.first_month
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key(['account_months.account_id', 'account_months.month_start']) }}
                                                                                as points_balance_account_key
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
