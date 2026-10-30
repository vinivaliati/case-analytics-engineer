-- Grão: 1 linha por segmento de exposição ao CRM no lançamento x histórico de resgate. PK: (exposure_segment, had_prior_redemption).
-- Testa a afirmação "a comunicação de lançamento explica o sucesso do Pix" de forma DESCRITIVA:
-- não há grupo de controle (control_group 100% vazio), então não mede efeito causal.
-- Janela de lançamento: 27/05 a 04/06/2026 (do lançamento ao fim da campanha CMP_LANCAMENTO_PIX).
with

customers as (
    select customer_key
    from {{ ref('dim_customer') }}
    where customer_key <> '-1'
)

, launch_campaign as (
    select campaign_key
    from {{ ref('dim_campaign') }}
    where campaign_name like 'CMP_LANCAMENTO_PIX%'
)

, launch_email as (
    select
        customer_key
        , bool_or(event_name = 'Notification Clicked')                  as clicked_launch_email
    from {{ ref('fct_crm_events') }}
    where campaign_key in (select campaign_key from launch_campaign)
    group by customer_key
    -- recebeu = teve envio efetivo; eventos de falha sozinhos não contam como recebimento
    having bool_or(event_name = 'Notification Sent')
)

, launch_window_exposure as (
    select
        customer_key
        , count(distinct campaign_key)                                  as campaigns_received
    from {{ ref('fct_crm_events') }}
    where event_name in ('Notification Sent', 'Push Impressions')
        and campaign_key <> '-1'
        and event_at >= cast('{{ var("pix_launch_date") }}' as timestamp)
        and event_at < cast('2026-06-05' as timestamp)
    group by customer_key
)

, redemptions as (
    select
        items.customer_key
        , items.item_created_at
        , products.is_pix
    from {{ ref('fct_redemption_items') }} as items
    inner join {{ ref('dim_product') }} as products
        on items.product_key = products.product_key
    where items.is_effective_redemption
)

, customer_flags as (
    select
        customers.customer_key
        , launch_email.customer_key is not null                                         as received_launch_email
        , coalesce(launch_email.clicked_launch_email, false)                            as clicked_launch_email
        , coalesce(launch_window_exposure.campaigns_received, 0)                        as campaigns_received
        , exists (
            select 1 from redemptions
            where redemptions.customer_key = customers.customer_key
                and redemptions.item_created_at < cast('{{ var("pix_launch_date") }}' as timestamp)
        )                                                                               as had_prior_redemption
        , exists (
            select 1 from redemptions
            where redemptions.customer_key = customers.customer_key
                and redemptions.is_pix
        )                                                                               as adopted_pix
    from customers
    left join launch_email
        on customers.customer_key = launch_email.customer_key
    left join launch_window_exposure
        on customers.customer_key = launch_window_exposure.customer_key
)

, final as (
    select
        case
            when received_launch_email and clicked_launch_email then '1. recebeu e clicou no e-mail de lançamento'
            when received_launch_email then '2. recebeu o e-mail de lançamento, não clicou'
            when campaigns_received > 0 then '3. não recebeu o e-mail, recebeu outra campanha'
            else '4. nenhuma comunicação na janela'
        end                                                                             as exposure_segment
        , had_prior_redemption
        , count(*)                                                                      as customers
        , count(*) filter (where adopted_pix)                                           as pix_adopters
        , round(100.0 * count(*) filter (where adopted_pix) / count(*), 2)              as pix_adoption_pct
    from customer_flags
    group by 1, 2
)

select * from final
