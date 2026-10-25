-- Grão: 1 linha por mês de referência do relatório do operador.
-- Números autodeclarados pelo operador: servem para reconciliar, não como fonte da verdade.
with

source as (
    select * from {{ source('operador', 'relatorio_mensal_cliente') }}
)

, renamed as (
    select
        cast(mes || '-01' as date)                                      as report_month
        , cast(aereas_pct as decimal(5, 2))                             as aereas_pct
        , cast(varejo_pct as decimal(5, 2))                             as varejo_pct
        , cast(nullif(pix_pct, '') as decimal(5, 2))                    as pix_pct
        , cast(nullif(pix_reais, '') as decimal(18, 2))                 as pix_brl
        , cast(cast(nullif(pix_pontos, '') as double) as bigint)        as pix_points
        , cast(cast(nullif(pix_transacoes, '') as double) as integer)   as pix_transactions
        , cast(emails_enviados as integer)                              as emails_sent
        , cast(cast(nullif(push_enviados, '') as double) as integer)    as push_sent
    from source
)

, deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by report_month
        order by report_month
    ) = 1
)

select * from deduplicated
