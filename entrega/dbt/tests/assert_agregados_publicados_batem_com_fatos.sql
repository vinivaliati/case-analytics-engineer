-- Os agregados publicados preservam os totais dos fatos de origem (nada perdido ou duplicado na agregação).
with

checks as (
    select
        'resgates: net_redeemed_points' as check_name
        , (select sum(net_redeemed_points) from {{ ref('agg_redemptions_monthly') }})    as published
        , (select sum(net_redeemed_points) from {{ ref('fct_redemption_items') }})       as source
    union all
    select
        'resgates: itens'
        , (select sum(items_count) from {{ ref('agg_redemptions_monthly') }})
        , (select count(*) from {{ ref('fct_redemption_items') }})
    union all
    select
        'resgates: product_value_brl'
        , (select sum(product_value_brl) from {{ ref('agg_redemptions_monthly') }})
        , (select sum(product_value_brl) from {{ ref('fct_redemption_items') }})
    union all
    select
        'ledger: points'
        , (select sum(points) from {{ ref('agg_points_movements_monthly') }})
        , (select sum(points) from {{ ref('fct_points_movements') }})
    union all
    select
        'ledger: movimentos'
        , (select sum(movements_count) from {{ ref('agg_points_movements_monthly') }})
        , (select count(*) from {{ ref('fct_points_movements') }})
    union all
    select
        'saldo: set/2026'
        , (select sum(closing_balance_points) from {{ ref('agg_points_balance_monthly') }} where month_date_key = 20260901)
        , (select sum(closing_balance_points) from {{ ref('fct_points_balance_monthly') }} where month_date_key = 20260901)
    union all
    select
        'crm: eventos'
        , (select sum(events_count) from {{ ref('agg_crm_events_monthly') }})
        , (select count(*) from {{ ref('fct_crm_events') }})
)

select *
from checks
where published is distinct from source
