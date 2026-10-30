-- Grão: 1 linha por mês com Pix. PK: month_start.
-- Reconcilia o Pix dos pedidos com o relatório do operador e testa a afirmação "o Pix sai a ~R$ 0,016 por ponto".
with

pix_items as (
    select
        dates.month_start
        , items.item_status
        , items.is_effective_redemption
        , items.paid_points
        , items.net_redeemed_points
        , items.product_value_brl
    from {{ ref('fct_redemption_items') }} as items
    inner join {{ ref('dim_product') }} as products
        on items.product_key = products.product_key
    inner join {{ ref('dim_date') }} as dates
        on items.item_date_key = dates.date_key
    where products.is_pix
)

, monthly as (
    select
        month_start
        , count(*) filter (where is_effective_redemption)                       as effective_transactions
        , sum(net_redeemed_points) filter (where is_effective_redemption)       as effective_points
        , sum(product_value_brl) filter (where is_effective_redemption)         as effective_brl
        , count(*)                                                              as all_status_transactions
        , sum(paid_points)                                                      as all_status_points
        , sum(product_value_brl)                                                as all_status_brl
        , count(*) filter (where not is_effective_redemption)                   as non_effective_transactions
        , sum(paid_points) filter (where not is_effective_redemption)           as non_effective_points
    from pix_items
    group by month_start
)

, operator as (
    select * from {{ ref('stg_operador__monthly_report') }}
)

, final as (
    select
        monthly.month_start
        , monthly.effective_transactions
        , monthly.effective_points
        , monthly.effective_brl
        , round(monthly.effective_brl / monthly.effective_points, 5)                as effective_brl_per_point
        , monthly.all_status_transactions
        , monthly.all_status_points
        , monthly.non_effective_transactions
        , monthly.non_effective_points
        , operator.pix_transactions                                                 as operator_transactions
        , operator.pix_points                                                       as operator_points
        , operator.pix_brl                                                          as operator_brl
        , round(operator.pix_brl / operator.pix_points, 5)                          as operator_brl_per_point
        , operator.pix_transactions = monthly.all_status_transactions               as operator_transactions_match_all_status
        , operator.pix_points = monthly.all_status_points                           as operator_points_match_all_status
        , round(operator.pix_brl - monthly.effective_brl, 2)                        as operator_brl_diff_vs_effective
        , round(100.0 * (operator.pix_brl - monthly.effective_brl) / monthly.effective_brl, 2)
                                                                                    as operator_brl_diff_vs_effective_pct
    from monthly
    left join operator
        on monthly.month_start = operator.report_month
)

select * from final
