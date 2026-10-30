-- Grão: 1 linha por mês. PK: month_start.
-- Participação de cada categoria nos pontos resgatados (resgate efetivo, líquido de devoluções),
-- nas visões contrato e estrita, comparada ao relatório do operador. Metas: aéreas >= 50%, varejo >= 20%.
with

redemptions as (
    select
        dates.month_start
        , dates.is_atypical_day
        , products.goal_category_contract
        , products.goal_category_strict
        , items.net_redeemed_points
    from {{ ref('fct_redemption_items') }} as items
    inner join {{ ref('dim_product') }} as products
        on items.product_key = products.product_key
    inner join {{ ref('dim_date') }} as dates
        on items.item_date_key = dates.date_key
    where items.is_effective_redemption
        and products.is_redemption
)

, monthly as (
    select
        month_start
        , sum(net_redeemed_points)                                                          as redeemed_points
        , sum(net_redeemed_points) filter (where goal_category_contract = 'aereas')         as aereas_points
        , sum(net_redeemed_points) filter (where goal_category_contract = 'varejo')         as varejo_points
        , coalesce(sum(net_redeemed_points) filter (where goal_category_contract = 'pix'), 0) as pix_points
        , sum(net_redeemed_points) filter (where goal_category_strict = 'varejo')           as varejo_strict_points
        , sum(net_redeemed_points) filter (where not is_atypical_day)                       as redeemed_points_ex_atypical
        , sum(net_redeemed_points) filter (
            where goal_category_contract = 'aereas' and not is_atypical_day)                as aereas_points_ex_atypical
    from redemptions
    group by month_start
)

, operator as (
    select * from {{ ref('stg_operador__monthly_report') }}
)

, final as (
    select
        monthly.month_start
        , monthly.redeemed_points
        , monthly.aereas_points
        , monthly.varejo_points
        , monthly.pix_points
        , round(100.0 * monthly.aereas_points / monthly.redeemed_points, 2)                as aereas_pct
        , round(100.0 * monthly.varejo_points / monthly.redeemed_points, 2)                as varejo_pct
        , round(100.0 * monthly.pix_points / monthly.redeemed_points, 2)                   as pix_pct
        , round(100.0 * monthly.varejo_strict_points / monthly.redeemed_points, 2)         as varejo_strict_pct
        , round(100.0 * monthly.aereas_points
            / nullif(monthly.redeemed_points - monthly.pix_points, 0), 2)                  as aereas_pct_ex_pix
        , round(100.0 * monthly.varejo_points
            / nullif(monthly.redeemed_points - monthly.pix_points, 0), 2)                  as varejo_pct_ex_pix
        , round(100.0 * monthly.aereas_points_ex_atypical
            / monthly.redeemed_points_ex_atypical, 2)                                      as aereas_pct_ex_atypical
        , 100.0 * monthly.aereas_points / monthly.redeemed_points >= 50                    as meets_aereas_goal
        , 100.0 * monthly.varejo_points / monthly.redeemed_points >= 20                    as meets_varejo_goal
        , operator.aereas_pct                                                              as operator_aereas_pct
        , operator.varejo_pct                                                              as operator_varejo_pct
        , operator.pix_pct                                                                 as operator_pix_pct
        , round(100.0 * monthly.aereas_points / monthly.redeemed_points
            - operator.aereas_pct, 2)                                                      as aereas_pct_diff_vs_operator
        , round(100.0 * monthly.varejo_points / monthly.redeemed_points
            - operator.varejo_pct, 2)                                                      as varejo_pct_diff_vs_operator
    from monthly
    left join operator
        on monthly.month_start = operator.report_month
)

select * from final
