-- Fato agregado publicado. Grão: mês x produto x nível de cartão (atual do cliente) x canal x status do item.
-- PK: redemption_agg_key. FKs: month_date_key, product_key, card_class_key.
-- Medidas aditivas apenas (contagem de clientes distintos não é aditiva e fica fora).
with

items as (
    select * from {{ ref('fct_redemption_items') }}
)

, customers as (
    select * from {{ ref('dim_customer') }}
)

, grouped as (
    select
        cast(strftime(date_trunc('month', items.item_created_at), '%Y%m%d') as integer)    as month_date_key
        , items.product_key
        , case
            when customers.current_card_class is null
                or customers.current_card_class = 'Desconhecido' then '-1'
            else {{ dbt_utils.generate_surrogate_key(['customers.current_card_class']) }}
          end                                                                               as card_class_key
        , items.sales_channel
        , items.item_status
        , items.is_effective_redemption
        , count(*)                                                                          as items_count
        , sum(items.net_redeemed_points)                                                    as net_redeemed_points
        , sum(items.points_debited)                                                         as points_debited
        , sum(coalesce(items.paid_points, 0))                                               as paid_points
        , sum(items.refunded_points)                                                        as refunded_points
        , sum(items.product_value_brl)                                                      as product_value_brl
        , sum(items.paid_brl)                                                               as customer_cash_brl
    from items
    left join customers
        on items.customer_key = customers.customer_key
    group by all
)

select
    {{ dbt_utils.generate_surrogate_key([
        'month_date_key', 'product_key', 'card_class_key', 'sales_channel', 'item_status', 'is_effective_redemption'
    ]) }}                                                                                   as redemption_agg_key
    , *
from grouped
