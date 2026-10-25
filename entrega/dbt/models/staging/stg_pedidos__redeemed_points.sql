-- Grão: 1 linha por movimento de pontos ligado a um item de pedido.
-- Não há chave natural: (order_item_id, movement_type) se repete sem que as linhas sejam idênticas.
-- Chave surrogate = hash de todas as colunas; o dedup remove só linhas 100% idênticas.
with

source as (
    select * from {{ source('pedidos', 'redeemed_points') }}
)

, renamed as (
    select
        {{ dbt_utils.generate_surrogate_key(['order_item_id', 'account_id', 'movement_type', 'points']) }}
                                                    as redeemed_point_key
        , cast(order_item_id as varchar)            as order_item_id
        , cast(account_id as varchar)               as account_id
        , cast(movement_type as varchar)            as movement_type
        , cast(points as bigint)                    as points
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by redeemed_point_key
        order by order_item_id
    ) = 1
)

select * from deduplicated
