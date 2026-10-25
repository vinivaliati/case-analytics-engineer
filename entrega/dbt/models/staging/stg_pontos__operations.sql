-- Grão: 1 linha por tipo de operação do ledger (operation_code).
with

source as (
    select * from {{ source('pontos', 'dim_operation') }}
)

, renamed as (
    select
        cast(operation_code as integer)             as operation_code
        , cast(operation_name as varchar)           as operation_name
        , cast(direction as varchar)                as direction
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by operation_code
        order by operation_name
    ) = 1
)

select * from deduplicated
