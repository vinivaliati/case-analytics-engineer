-- Grão: 1 linha por tipo de operação do ledger. PK: operation_key.
with

operations as (
    select * from {{ ref('stg_pontos__operations') }}
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key(['operation_code']) }}  as operation_key
        , operation_code
        , operation_name
        , direction
        , operation_name like '%MIGRACAO'                           as is_migration
        , operation_name like 'EXPIRACAO%'                          as is_expiration
    from operations
)

select * from final
