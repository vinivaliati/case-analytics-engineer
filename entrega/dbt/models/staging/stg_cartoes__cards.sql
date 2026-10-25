-- Grão: 1 linha por conta de cartão (account_id). Um usuário pode ter várias contas.
with

source as (
    select * from {{ source('cartoes', 'cards') }}
)

, renamed as (
    select
        cast(account_id as varchar)                 as account_id
        , cast(user_id as varchar)                  as user_id
        , cast(card_class as varchar)               as card_class
        , cast(card_flag as varchar)                as card_brand
        , {{ to_local_ts('created_at') }}           as card_created_at
        , cast(is_most_recent as boolean)           as is_most_recent
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by account_id
        order by card_created_at desc
    ) = 1
)

select * from deduplicated
