-- Grão: 1 linha por mês. PK: month_start.
-- Fluxo de pontos do programa (emissão, resgate, expiração, saldo em aberto) e indicadores de breakage.
-- Definição de mercado (docs/benchmark_breakage.md): breakage = expirados / emitidos, por origem.
-- expired_to_redeemed_pct NÃO é breakage: existe para testar a hipótese de origem do "40%" da diretoria.
with

monthly as (
    select
        month_start
        , sum(credited_points)                  as credited_points
        , sum(migrated_points)                  as migrated_points
        , sum(redeemed_points)                  as redeemed_points
        , sum(order_refund_points)              as order_refund_points
        , sum(expired_points)                   as expired_points
        , sum(expired_migrated_points)          as expired_migrated_points
        , sum(closing_balance_points)           as closing_balance_points
    from {{ ref('fct_points_balance_monthly') }}
    group by month_start
)

, cumulative as (
    select
        *
        , sum(credited_points) over (order by month_start)            as cum_credited_points
        , sum(migrated_points) over (order by month_start)            as cum_migrated_points
        , sum(expired_points) over (order by month_start)             as cum_expired_points
        , sum(expired_migrated_points) over (order by month_start)    as cum_expired_migrated_points
        , lag(closing_balance_points) over (order by month_start)     as opening_balance_points
    from monthly
)

, final as (
    select
        month_start
        , credited_points
        , migrated_points
        , redeemed_points
        , order_refund_points
        , expired_points
        , expired_migrated_points
        , expired_points + expired_migrated_points                                          as total_expired_points
        , opening_balance_points
        , closing_balance_points
        , cum_credited_points
        , cum_migrated_points
        , round(100.0 * cum_expired_points / nullif(cum_credited_points, 0), 2)            as breakage_new_program_realized_pct
        , round(100.0 * cum_expired_migrated_points / nullif(cum_migrated_points, 0), 2)   as breakage_migrated_realized_pct
        , round(100.0 * (expired_points + expired_migrated_points)
            / nullif(opening_balance_points, 0), 2)                                        as expiration_rate_on_opening_balance_pct
        , round(100.0 * (expired_points + expired_migrated_points)
            / nullif(redeemed_points, 0), 2)                                               as expired_to_redeemed_pct
    from cumulative
)

select * from final
