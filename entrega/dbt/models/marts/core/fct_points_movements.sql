-- Fato transacional. Grão: 1 linha por movimento do ledger. PK: movement_id.
-- FKs: account_key, customer_key, operation_key, movement_date_key, valid_until_date_key (nulo em débitos).
with

ledger as (
    select * from {{ ref('stg_pontos__points_ledger') }}
)

, final as (
    select
        movement_id
        , {{ dbt_utils.generate_surrogate_key(['account_id']) }}        as account_key
        , {{ dbt_utils.generate_surrogate_key(['user_id']) }}           as customer_key
        , {{ dbt_utils.generate_surrogate_key(['operation_code']) }}    as operation_key
        , cast(strftime(movement_at, '%Y%m%d') as integer)              as movement_date_key
        , cast(strftime(valid_until, '%Y%m%d') as integer)              as valid_until_date_key
        , movement_at
        , valid_until
        , points
        , greatest(points, 0)                                           as credit_points
        , greatest(-points, 0)                                          as debit_points
    from ledger
)

select * from final
