-- Grão: 1 linha por combinação fornecedor x responsável x tipo de produto x categoria macro. PK: product_key.
-- A classificação para as metas contratuais (aéreas/varejo) ainda está em decisão e entra aqui depois.
with

items as (
    select * from {{ ref('stg_pedidos__order_items') }}
)

, products as (
    select distinct
        supplier_name
        , supplier_responsible
        , product_type
        , category_macro
    from items
)

, final as (
    select
        {{ dbt_utils.generate_surrogate_key([
            'supplier_name', 'supplier_responsible', 'product_type', 'category_macro'
        ]) }}                                           as product_key
        , supplier_name
        , supplier_responsible
        , product_type
        , category_macro
        , supplier_name = 'Pix Pontua+'                 as is_pix
        , product_type = 'COMPRA_PONTOS'                as is_points_purchase
    from products
)

select * from final
