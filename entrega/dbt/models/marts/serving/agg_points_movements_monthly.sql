-- Fato agregado publicado. Grão: mês x operação do ledger x nível de cartão (atual do cliente).
-- PK: points_movement_agg_key. FKs: month_date_key, operation_key, card_class_key.
with

movements as (
    select * from {{ ref('fct_points_movements') }}
)

, customers as (
    select * from {{ ref('dim_customer') }}
)

, grouped as (
    select
        cast(strftime(date_trunc('month', movements.movement_at), '%Y%m%d') as integer)   as month_date_key
        , movements.operation_key
        , case
            when customers.current_card_class is null then '-1'
            else {{ dbt_utils.generate_surrogate_key(['customers.current_card_class']) }}
          end                                                                               as card_class_key
        , count(*)                                                                          as movements_count
        , sum(movements.points)                                                             as points
        , sum(movements.credit_points)                                                      as credit_points
        , sum(movements.debit_points)                                                       as debit_points
    from movements
    left join customers
        on movements.customer_key = customers.customer_key
    group by all
)

select
    {{ dbt_utils.generate_surrogate_key(['month_date_key', 'operation_key', 'card_class_key']) }}
                                                                                            as points_movement_agg_key
    , *
from grouped
