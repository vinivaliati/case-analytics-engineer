-- Fato agregado publicado. Grão: mês x campanha x tipo de evento x canal.
-- PK: crm_event_agg_key. FKs: month_date_key, campaign_key.
with

events as (
    select * from {{ ref('fct_crm_events') }}
)

, grouped as (
    select
        cast(strftime(date_trunc('month', event_at), '%Y%m%d') as integer)    as month_date_key
        , campaign_key
        , event_name
        , coalesce(campaign_type, 'Sem canal')                                as campaign_type
        , sum(event_count)                                                    as events_count
    from events
    group by all
)

select
    {{ dbt_utils.generate_surrogate_key(['month_date_key', 'campaign_key', 'event_name', 'campaign_type']) }}
                                                                                as crm_event_agg_key
    , *
from grouped
