-- Hipótese a confirmar: no ledger, CREDIT tem points > 0 e DEBIT tem points < 0.
-- Retorna os movimentos que violam a regra. Se falhar, a soma de saldo precisa usar direction, não o sinal.
select
    ledger.movement_id
    , ledger.operation_code
    , operations.direction
    , ledger.points
from {{ ref('stg_pontos__points_ledger') }} as ledger
inner join {{ ref('stg_pontos__operations') }} as operations
    on ledger.operation_code = operations.operation_code
where (operations.direction = 'CREDIT' and ledger.points <= 0)
    or (operations.direction = 'DEBIT' and ledger.points >= 0)
