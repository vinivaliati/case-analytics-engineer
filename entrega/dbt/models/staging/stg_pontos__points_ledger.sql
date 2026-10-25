-- Grão: 1 linha por movimento no saldo de pontos (movement_id).
-- points tem sinal: positivo = crédito, negativo = débito (conferido contra dim_operation.direction nos testes).
with

source as (
    select * from {{ source('pontos', 'points_ledger') }}
)

, renamed as (
    select
        cast(movement_id as varchar)                as movement_id
        , cast(user_id as varchar)                  as user_id
        , cast(account_id as varchar)               as account_id
        , cast(operation_code as integer)           as operation_code
        , cast(cast(points as double) as bigint)    as points
        , {{ to_local_ts('movement_at') }}          as movement_at
        , cast(nullif(valid_until, '') as date)     as valid_until
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by movement_id
        order by movement_at desc
    ) = 1
)

select * from deduplicated
