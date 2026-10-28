-- Grão: 1 linha por métrica de perfil dos dados. PK: metric.
-- Torna reproduzíveis as descobertas da exploração inicial (citadas no README e na apresentação).
-- Só contagens agregadas: nenhum identificador de cliente, conta ou pedido.
with

orders as (
    select * from {{ ref('stg_pedidos__orders') }}
)

, carts as (
    select * from {{ ref('stg_pedidos__carts') }}
)

, crm as (
    select * from {{ ref('stg_crm__events') }}
)

-- Fuso do CRM: para cada 'Order Approved', a diferença (em horas, arredondada) entre o horário bruto do CRM
-- e o pedido mais próximo do mesmo cliente no sistema de pedidos (horário local).
, crm_order_events as (
    select
        crm.crm_event_key
        , crm.user_id
        , crm.event_at_utc
    from crm
    where crm.event_name = 'Order Approved'
        and crm.user_id is not null
)

, crm_nearest_order as (
    select
        crm_order_events.crm_event_key
        , min_by(
            datediff('minute', orders.order_created_at, crm_order_events.event_at_utc)
            , abs(datediff('minute', orders.order_created_at, crm_order_events.event_at_utc))
        )                                                               as minutes_after_order
    from crm_order_events
    inner join carts
        on crm_order_events.user_id = carts.user_id
    inner join orders
        on carts.cart_id = orders.cart_id
    group by crm_order_events.crm_event_key
)

, paying_accounts as (
    select
        redeemed.order_item_id
        , count(distinct redeemed.account_id)                           as accounts
        , count(distinct accounts.card_class)                           as card_classes
    from {{ ref('stg_pedidos__redeemed_points') }} as redeemed
    inner join {{ ref('stg_cartoes__cards') }} as accounts
        on redeemed.account_id = accounts.account_id
    where redeemed.movement_type = 'RESGATE'
    group by redeemed.order_item_id
)

, atypical_day as (
    select
        count(*)                                                        as items
        , sum(items.net_redeemed_points)                                as points
    from {{ ref('fct_redemption_items') }} as items
    inner join {{ ref('dim_product') }} as products
        on items.product_key = products.product_key
    inner join {{ ref('dim_date') }} as dates
        on items.item_date_key = dates.date_key
    where dates.is_atypical_day
        and products.goal_category_contract = 'aereas'
        and items.is_effective_redemption
)

, metrics as (
    select 'orders_user_id_null_pct' as metric
        , round(100.0 * count(*) filter (where user_id is null) / count(*), 2) as value
        , '% de pedidos com user_id vazio (o cliente vem de carts)' as description
    from orders

    union all
    select 'crm_order_approved_events', count(*), 'Eventos Order Approved do CRM com cliente'
    from crm_nearest_order

    union all
    select 'crm_events_3h_after_order', count(*) filter (where round(minutes_after_order / 60.0) = 3)
        , 'Order Approved exatamente 3h depois do pedido: confirma que o CRM grava em UTC'
    from crm_nearest_order

    union all
    select 'crm_events_without_customer', count(*) filter (where user_id is null)
        , 'Eventos de CRM sem user_id (ligados ao membro desconhecido -1)'
    from crm

    union all
    select 'crm_control_group_null_pct', round(100.0 * count(*) filter (where control_group is null) / count(*), 2)
        , '% de eventos de CRM sem grupo de controle'
    from crm

    union all
    select 'items_paid_by_multiple_accounts', count(*) filter (where accounts > 1)
        , 'Itens pagos com pontos de mais de uma conta do mesmo cliente'
    from paying_accounts

    union all
    select 'items_paid_by_mixed_card_classes', count(*) filter (where card_classes > 1)
        , 'Itens pagos por contas de níveis de cartão diferentes'
    from paying_accounts

    union all
    select 'items_points_reconciled', count(*)
        , 'Itens APROVADO/ESTORNADO em que os pontos debitados = pontos pagos no pedido'
    from {{ ref('fct_redemption_items') }}
    where item_status in ('APROVADO', 'ESTORNADO')
        and points_debited = paid_points

    union all
    select 'accounts_negative_balance_last_month', count(*) filter (where closing_balance_points < 0)
        , 'Contas com saldo negativo em set/2026 (o saldo é por cliente, não por conta)'
    from {{ ref('fct_points_balance_account_monthly') }}
    where month_start = (select max(month_start) from {{ ref('fct_points_balance_account_monthly') }})

    union all
    select 'customers_negative_balance_last_month', count(*) filter (where closing_balance_points < 0)
        , 'Clientes com saldo negativo em set/2026'
    from {{ ref('fct_points_balance_monthly') }}
    where month_start = (select max(month_start) from {{ ref('fct_points_balance_monthly') }})

    union all
    select 'customers', count(*), 'Clientes na base'
    from {{ ref('dim_customer') }}
    where customer_key <> '-1'

    union all
    select 'accounts', count(*), 'Contas de cartão na base'
    from {{ ref('dim_account') }}
    where account_key <> '-1'

    union all
    select 'atypical_day_air_items', items, 'Resgates aéreos efetivos em 12/01/2026 (dia atípico)'
    from atypical_day

    union all
    select 'atypical_day_air_points', points, 'Pontos resgatados em aéreas em 12/01/2026'
    from atypical_day
)

select
    metric
    , cast(value as double)                                             as value
    , description
from metrics
