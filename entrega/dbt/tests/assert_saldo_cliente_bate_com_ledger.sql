-- O saldo de cada cliente no último mês do snapshot = soma de todos os movimentos dele no ledger.
with

snapshot_last as (
    select
        customer_key
        , closing_balance_points
    from {{ ref('fct_points_balance_monthly') }}
    qualify row_number() over (partition by customer_key order by month_date_key desc) = 1
)

, ledger as (
    select
        customer_key
        , sum(points) as ledger_balance_points
    from {{ ref('fct_points_movements') }}
    group by customer_key
)

select
    coalesce(snapshot_last.customer_key, ledger.customer_key) as customer_key
    , snapshot_last.closing_balance_points
    , ledger.ledger_balance_points
from snapshot_last
full outer join ledger
    on snapshot_last.customer_key = ledger.customer_key
where snapshot_last.closing_balance_points is distinct from ledger.ledger_balance_points
