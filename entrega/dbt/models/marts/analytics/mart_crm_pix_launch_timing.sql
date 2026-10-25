-- Grão: 1 linha por janela de tempo entre o e-mail de lançamento e o primeiro Pix. PK: timing_window.
-- Só clientes que receberam o e-mail de lançamento (envio efetivo) e usaram o Pix. Descritivo.
with

launch_sent as (
    select
        events.customer_key
        , min(events.event_at)                      as first_sent_at
    from {{ ref('fct_crm_events') }} as events
    inner join {{ ref('dim_campaign') }} as campaigns
        on events.campaign_key = campaigns.campaign_key
    where campaigns.campaign_name like 'CMP_LANCAMENTO_PIX%'
        and events.event_name = 'Notification Sent'
    group by events.customer_key
)

, first_pix as (
    select
        items.customer_key
        , min(items.item_created_at)                as first_pix_at
    from {{ ref('fct_redemption_items') }} as items
    inner join {{ ref('dim_product') }} as products
        on items.product_key = products.product_key
    where products.is_pix
        and items.is_effective_redemption
    group by items.customer_key
)

, classified as (
    select
        case
            when first_pix.first_pix_at < launch_sent.first_sent_at then '0. Pix antes do e-mail'
            when first_pix.first_pix_at < launch_sent.first_sent_at + interval 7 day then '1. até 7 dias'
            when first_pix.first_pix_at < launch_sent.first_sent_at + interval 30 day then '2. 8 a 30 dias'
            else '3. mais de 30 dias'
        end                                         as timing_window
    from launch_sent
    inner join first_pix
        on launch_sent.customer_key = first_pix.customer_key
)

select
    timing_window
    , count(*)                                                      as customers
    , round(100.0 * count(*) / sum(count(*)) over (), 2)            as customers_pct
from classified
group by timing_window
