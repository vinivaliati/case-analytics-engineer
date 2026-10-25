-- Grão: 1 linha por evento do CRM.
-- event_ts chega em UTC sem offset; convertido para o fuso local do projeto.
-- Não há chave natural: chave surrogate = hash de todas as colunas; dedup remove só linhas idênticas.
with

source as (
    select * from {{ source('crm', 'crm_events') }}
)

, renamed as (
    select
        {{ dbt_utils.generate_surrogate_key([
            'event_ts', 'user_id', 'device_id', 'event_name'
            , 'campaign_type', 'campaign_id', 'control_group', 'event_properties'
        ]) }}                                           as crm_event_key
        , {{ utc_to_local_ts('event_ts') }}             as event_at
        , cast(event_ts as timestamp)                   as event_at_utc
        , cast(nullif(user_id, '') as varchar)          as user_id
        , cast(device_id as varchar)                    as device_id
        , cast(event_name as varchar)                   as event_name
        , cast(nullif(campaign_type, '') as varchar)    as campaign_type
        , cast(nullif(campaign_id, '') as varchar)      as campaign_id
        , cast(nullif(control_group, '') as varchar)    as control_group
        , cast(event_properties as json)                as event_properties
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by crm_event_key
        order by event_at
    ) = 1
)

select * from deduplicated
