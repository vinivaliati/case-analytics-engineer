-- Fato transacional. Grão: 1 linha por item de pedido. PK: order_item_id.
-- FKs: product_key, customer_key, item_date_key. A conta que pagou não entra aqui porque
-- 1.471 itens são pagos por mais de uma conta (ver decisões pendentes).
-- Inclui todos os status: o filtro de "resgate efetivo" é regra de negócio e fica para as camadas de consumo.
with

items as (
    select * from {{ ref('stg_pedidos__order_items') }}
)

, orders as (
    select * from {{ ref('stg_pedidos__orders') }}
)

, carts as (
    select * from {{ ref('stg_pedidos__carts') }}
)

, redeemed as (
    select * from {{ ref('int_redeemed_points__per_item') }}
)

, final as (
    select
        items.order_item_id
        , items.order_id
        , {{ dbt_utils.generate_surrogate_key([
            'items.supplier_name', 'items.supplier_responsible', 'items.product_type', 'items.category_macro'
        ]) }}                                                           as product_key
        , case
            when carts.user_id is null then '-1'
            else {{ dbt_utils.generate_surrogate_key(['carts.user_id']) }}
          end                                                     as customer_key
        , cast(strftime(items.item_created_at, '%Y%m%d') as integer)    as item_date_key
        , items.item_created_at
        , items.item_status
        , orders.order_status
        , carts.sales_channel
        , items.paid_points
        , items.paid_brl
        , items.product_value_brl
        , items.refunded_points
        , items.quantity
        , coalesce(redeemed.points_debited, 0)                          as points_debited
        , coalesce(redeemed.paying_accounts_count, 0)                   as paying_accounts_count
        , coalesce(redeemed.reservation_net_points, 0)                  as reservation_net_points
    from items
    inner join orders
        on items.order_id = orders.order_id
    left join carts
        on orders.cart_id = carts.cart_id
    left join redeemed
        on items.order_item_id = redeemed.order_item_id
)

select * from final
