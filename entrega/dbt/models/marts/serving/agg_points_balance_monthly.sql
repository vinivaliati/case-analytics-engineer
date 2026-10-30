-- Snapshot agregado publicado. Grão: mês x nível de cartão (atual do cliente).
-- PK: points_balance_agg_key. FKs: month_date_key, card_class_key.
-- closing_balance_points é semi-aditivo: soma entre níveis, nunca entre meses.
with

balances as (
    select * from {{ ref('fct_points_balance_monthly') }}
)

, customers as (
    select * from {{ ref('dim_customer') }}
)

, grouped as (
    select
        balances.month_date_key
        , case
            when customers.current_card_class is null then '-1'
            else {{ dbt_utils.generate_surrogate_key(['customers.current_card_class']) }}
          end                                                                   as card_class_key
        , count(*)                                                              as customers_in_program
        , count(*) filter (where balances.closing_balance_points > 0)           as customers_with_balance
        , sum(balances.closing_balance_points)                                  as closing_balance_points
        , sum(balances.credited_points)                                         as credited_points
        , sum(balances.migrated_points)                                         as migrated_points
        , sum(balances.redeemed_points)                                         as redeemed_points
        , sum(balances.order_refund_points)                                     as order_refund_points
        , sum(balances.expired_points)                                          as expired_points
        , sum(balances.expired_migrated_points)                                 as expired_migrated_points
    from balances
    left join customers
        on balances.customer_key = customers.customer_key
    group by all
)

select
    {{ dbt_utils.generate_surrogate_key(['month_date_key', 'card_class_key']) }}  as points_balance_agg_key
    , *
from grouped
