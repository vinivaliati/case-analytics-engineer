-- Grão: 1 linha por pedido (order_id).
-- user_id vem 100% vazio na origem: o usuário do pedido deve vir de carts.
with

source as (
    select * from {{ source('pedidos', 'orders') }}
)

, renamed as (
    select
        cast(order_id as varchar)                   as order_id
        , cast(cart_id as varchar)                  as cart_id
        , cast(nullif(user_id, '') as varchar)      as user_id
        , {{ to_local_ts('created_at') }}           as order_created_at
        , cast(status as varchar)                   as order_status
        , {{ to_local_ts('status_updated_at') }}    as order_status_updated_at
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by order_id
        order by order_status_updated_at desc
    ) = 1
)

select * from deduplicated
