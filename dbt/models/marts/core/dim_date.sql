-- Grão: 1 linha por dia do calendário. PK: date_key (inteiro yyyymmdd).
with

days as (
    select cast(range as date) as date_day
    from range(
        cast('{{ var("calendar_start") }}' as date)
        , cast('{{ var("calendar_end") }}' as date) + interval 1 day
        , interval 1 day
    )
)

, final as (
    select
        cast(strftime(date_day, '%Y%m%d') as integer)                   as date_key
        , date_day
        , cast(date_trunc('month', date_day) as date)                   as month_start
        , strftime(date_day, '%Y-%m')                                   as year_month
        , year(date_day)                                                as year
        , quarter(date_day)                                             as quarter
        , month(date_day)                                               as month
        , isodow(date_day)                                              as iso_day_of_week
        , date_day >= cast('{{ var("pix_launch_date") }}' as date)      as is_after_pix_launch
        , date_day < cast('{{ var("extraction_date") }}' as date)       as is_before_extraction
    from days
)

select * from final
