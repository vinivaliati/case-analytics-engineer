-- Grão: 1 linha por combinação fornecedor x responsável x tipo de produto x categoria macro. PK: product_key.
-- A classificação das metas vem do seed goal_categories (regra de negócio versionada e revisável).
with

items as (
    select * from {{ ref('stg_pedidos__order_items') }}
)

, goal_categories as (
    select * from {{ ref('goal_categories') }}
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
            'products.supplier_name', 'products.supplier_responsible'
            , 'products.product_type', 'products.category_macro'
        ]) }}                                                   as product_key
        , products.supplier_name
        , products.supplier_responsible
        , products.product_type
        , products.category_macro
        , goal_categories.goal_category_contract
        , goal_categories.goal_category_strict
        , goal_categories.is_redemption
        , goal_categories.rationale                             as goal_category_rationale
        , products.supplier_name = 'Pix Pontua+'                as is_pix
        , products.product_type = 'COMPRA_PONTOS'               as is_points_purchase
    from products
    left join goal_categories
        on products.supplier_name = goal_categories.supplier_name
        and products.product_type = goal_categories.product_type
)

select * from final
