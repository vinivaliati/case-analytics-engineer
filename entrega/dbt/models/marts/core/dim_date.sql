-- Grão: 1 linha por dia do calendário. PK: date_key (inteiro yyyymmdd).
-- Eventos de negócio (lançamentos, dias atípicos) vêm da tabela de referência calendar_events.
with

days as (
    select cast(range as date) as date_day
    from range(
        cast('{{ var("calendar_start") }}' as date)
        , cast('{{ var("calendar_end") }}' as date) + interval 1 day
        , interval 1 day
    )
)

, calendar_events as (
    select * from {{ ref('calendar_events') }}
)

, final as (
    select
        cast(strftime(days.date_day, '%Y%m%d') as integer)                          as date_key
        , days.date_day
        , cast(date_trunc('month', days.date_day) as date)                          as month_start
        , strftime(days.date_day, '%Y-%m')                                          as year_month
        , year(days.date_day)                                                       as year
        , quarter(days.date_day)                                                    as quarter
        , month(days.date_day)                                                      as month
        , isodow(days.date_day)                                                     as iso_day_of_week
        , days.date_day >= cast('{{ var("pix_launch_date") }}' as date)             as is_after_pix_launch
        , days.date_day between cast('{{ var("baseline_start") }}' as date)
            and cast('{{ var("pix_launch_date") }}' as date) - interval 1 day       as is_pre_pix_baseline
        , days.date_day < cast('{{ var("extraction_date") }}' as date)              as is_before_extraction
        , coalesce(calendar_events.event_type = 'atipico', false)                   as is_atypical_day
        , calendar_events.event_name
        , calendar_events.evidence_status                                           as event_evidence_status
    from days
    left join calendar_events
        on days.date_day = calendar_events.event_date
)

select * from final
