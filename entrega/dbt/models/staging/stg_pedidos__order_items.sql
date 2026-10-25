-- Grão: 1 linha por item de pedido (order_item_id). quantity é sempre 1 na v1.
with

source as (
    select * from {{ source('pedidos', 'order_items') }}
)

, renamed as (
    select
        cast(order_item_id as varchar)                              as order_item_id
        , cast(order_id as varchar)                                 as order_id
        , {{ to_local_ts('created_at') }}                           as item_created_at
        , cast(status as varchar)                                   as item_status
        , cast(product_type as varchar)                             as product_type
        , cast(supplier_name as varchar)                            as supplier_name
        , cast(supplier_responsible as varchar)                     as supplier_responsible
        , cast(category_macro as varchar)                           as category_macro
        , cast(cast(nullif(paid_points, '') as double) as bigint)   as paid_points
        , cast(paid_currency as decimal(18, 2))                     as paid_brl
        , cast(product_value as decimal(18, 2))                     as product_value_brl
        , cast(cast(refunded_points as double) as bigint)           as refunded_points
        , cast(quantity as integer)                                 as quantity
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by order_item_id
        order by item_created_at desc
    ) = 1
)

select * from deduplicated
