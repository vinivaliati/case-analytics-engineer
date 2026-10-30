-- O saldo de cada conta no último mês do snapshot de contas = soma de todos os movimentos dela no ledger.
with

snapshot_last as (
    select
        account_key
        , closing_balance_points
    from {{ ref('fct_points_balance_account_monthly') }}
    qualify row_number() over (partition by account_key order by month_date_key desc) = 1
)

, ledger as (
    select
        account_key
        , sum(points) as ledger_balance_points
    from {{ ref('fct_points_movements') }}
    group by account_key
)

select
    coalesce(snapshot_last.account_key, ledger.account_key) as account_key
    , snapshot_last.closing_balance_points
    , ledger.ledger_balance_points
from snapshot_last
full outer join ledger
    on snapshot_last.account_key = ledger.account_key
where snapshot_last.closing_balance_points is distinct from ledger.ledger_balance_points
