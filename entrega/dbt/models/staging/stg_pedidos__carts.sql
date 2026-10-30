-- Grão: 1 linha por carrinho (cart_id). Fonte do user_id dos pedidos.
with

source as (
    select * from {{ source('pedidos', 'carts') }}
)

, renamed as (
    select
        cast(cart_id as varchar)                    as cart_id
        , cast(user_id as varchar)                  as user_id
        , cast(channel as varchar)                  as sales_channel
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by cart_id
        order by user_id
    ) = 1
)

select * from deduplicated
