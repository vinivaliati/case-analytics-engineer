-- Dimensão publicada. Grão: 1 linha por mês com dados (até a extração). PK: month_date_key (yyyymm01).
-- Conformada com dim_date: month_date_key = date_key do primeiro dia do mês.
with

days as (
    select * from {{ ref('dim_date') }}
    where is_before_extraction
)

, final as (
    select
        cast(strftime(month_start, '%Y%m%d') as integer)                    as month_date_key
        , month_start
        , any_value(year_month)                                             as year_month
        , any_value(year)                                                   as year
        , any_value(quarter)                                                as quarter
        , any_value(month)                                                  as month
        , case
            when max(date_day) < cast('{{ var("pix_launch_date") }}' as date) then 'antes_do_pix'
            when min(date_day) < cast('{{ var("pix_launch_date") }}' as date) then 'mes_do_lancamento'
            else 'depois_do_pix'
          end                                                               as pix_phase
        , bool_or(is_pre_pix_baseline)                                      as is_in_pre_pix_baseline
        , bool_or(is_atypical_day)                                          as has_atypical_day
        , string_agg(event_name, '; ') filter (where event_name is not null) as month_events
    from days
    group by month_start
)

select * from final
