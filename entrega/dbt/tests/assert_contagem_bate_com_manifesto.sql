-- Garante que os CSVs lidos são a versão v1 descrita no MANIFESTO (contagem de linhas por arquivo).
-- Retorna as tabelas cuja contagem diverge. O hash SHA-256 é conferido no scripts/build.py.
with

manifesto as (
    select
        replace(arquivo, '.csv', '')        as tabela
        , cast(linhas as bigint)            as linhas_esperadas
    from {{ source('controle', 'MANIFESTO_v1') }}
)

, contagens as (
    select 'cards' as tabela, count(*) as linhas_lidas from {{ source('cartoes', 'cards') }}
    union all select 'carts', count(*) from {{ source('pedidos', 'carts') }}
    union all select 'crm_events', count(*) from {{ source('crm', 'crm_events') }}
    union all select 'dim_operation', count(*) from {{ source('pontos', 'dim_operation') }}
    union all select 'order_items', count(*) from {{ source('pedidos', 'order_items') }}
    union all select 'orders', count(*) from {{ source('pedidos', 'orders') }}
    union all select 'points_ledger', count(*) from {{ source('pontos', 'points_ledger') }}
    union all select 'redeemed_points', count(*) from {{ source('pedidos', 'redeemed_points') }}
    union all select 'relatorio_mensal_cliente', count(*) from {{ source('operador', 'relatorio_mensal_cliente') }}
)

select
    manifesto.tabela
    , manifesto.linhas_esperadas
    , contagens.linhas_lidas
from manifesto
full outer join contagens
    on manifesto.tabela = contagens.tabela
where manifesto.linhas_esperadas is distinct from contagens.linhas_lidas
