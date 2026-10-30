-- Grão: 1 linha por período (antes do Pix / depois do Pix) x categoria estrita de meta. PK: (period, goal_category_strict).
-- Custo por ponto de cada modalidade e volume mensal médio, para avaliar a saúde financeira.
-- HIPÓTESE: o custo do programa por ponto ~ (valor do produto - dinheiro pago pelo cliente) / pontos.
-- Para varejo de parceiros do grupo, o custo real tende a ser menor que o valor de prateleira.
-- O preço que o banco paga por ponto não está nos dados; o enunciado diz que é menor que o custo de aéreas.
with

redemptions as (
    select
        case
            when dates.is_pre_pix_baseline then 'antes_do_pix'
            when dates.is_after_pix_launch then 'depois_do_pix'
        end                                         as period
        , products.goal_category_strict
        , items.net_redeemed_points
        , items.product_value_brl
        , items.paid_brl
    from {{ ref('fct_redemption_items') }} as items
    inner join {{ ref('dim_product') }} as products
        on items.product_key = products.product_key
    inner join {{ ref('dim_date') }} as dates
        on items.item_date_key = dates.date_key
    where items.is_effective_redemption
        and products.is_redemption
        and (dates.is_pre_pix_baseline or dates.is_after_pix_launch)
        and dates.is_before_extraction
)

, period_days as (
    select
        case
            when is_pre_pix_baseline then 'antes_do_pix'
            when is_after_pix_launch then 'depois_do_pix'
        end                                         as period
        , count(*)                                  as days
    from {{ ref('dim_date') }}
    where (is_pre_pix_baseline or is_after_pix_launch)
        and is_before_extraction
    group by 1
)

, final as (
    select
        redemptions.period
        , redemptions.goal_category_strict
        , count(*)                                                                              as redemptions
        , sum(redemptions.net_redeemed_points)                                                  as redeemed_points
        , round(sum(redemptions.net_redeemed_points) * 30.4 / any_value(period_days.days))      as avg_monthly_points
        , sum(redemptions.product_value_brl)                                                    as product_value_brl
        , sum(redemptions.paid_brl)                                                             as customer_cash_brl
        , round(sum(redemptions.product_value_brl) / sum(redemptions.net_redeemed_points), 5)   as value_per_point_brl
        , round(sum(redemptions.product_value_brl - redemptions.paid_brl)
            / sum(redemptions.net_redeemed_points), 5)                                          as cost_per_point_brl
        , any_value(period_days.days)                                                           as period_days
    from redemptions
    inner join period_days
        on redemptions.period = period_days.period
    group by redemptions.period, redemptions.goal_category_strict
)

select * from final
