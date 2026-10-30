-- Fato transacional. Grão: 1 linha por evento do CRM. PK: crm_event_key.
-- FKs: customer_key ('-1' quando user_id vazio), campaign_key ('-1' sem campanha), event_date_key (data local).
with

events as (
    select * from {{ ref('stg_crm__events') }}
)

, final as (
    select
        crm_event_key
        , case
            when user_id is null then '-1'
            else {{ dbt_utils.generate_surrogate_key(['user_id']) }}
          end                                                     as customer_key
        , case
            when campaign_id is null then '-1'
            else {{ dbt_utils.generate_surrogate_key(['campaign_id']) }}
          end                                                           as campaign_key
        , cast(strftime(event_at, '%Y%m%d') as integer)                 as event_date_key
        , event_at
        , event_at_utc
        , device_id
        , event_name
        , campaign_type
        , event_properties
        , 1                                                             as event_count
    from events
)

select * from final
