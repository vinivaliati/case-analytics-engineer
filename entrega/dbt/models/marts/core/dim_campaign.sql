-- Grão: 1 linha por campanha do CRM (campaign_id). PK: campaign_key. Linha '-1' = sem campanha (ex.: Order Approved).
-- Uma campanha pode rodar em mais de um canal (27 campanhas na v1): o canal fica no fato (campaign_type).
with

events as (
    select * from {{ ref('stg_crm__events') }}
    where campaign_id is not null
)

, campaigns as (
    select
        campaign_id
        , mode(event_properties ->> 'campaign_name')                as campaign_name
        , string_agg(distinct campaign_type, ', ' order by campaign_type) as campaign_channels
        , min(event_at)                                             as first_event_at
        , max(event_at)                                             as last_event_at
    from events
    group by campaign_id
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key(['campaign_id']) }}     as campaign_key
        , campaign_id
        , campaign_name
        , campaign_channels
        , first_event_at
        , last_event_at
    from campaigns
)

, unknown_member as (
    select
        '-1'                                as campaign_key
        , null                              as campaign_id
        , 'Sem campanha'                    as campaign_name
        , null                              as campaign_channels
        , null                              as first_event_at
        , null                              as last_event_at
)

select * from final
union all
select * from unknown_member
