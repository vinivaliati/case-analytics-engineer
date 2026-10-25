{#- Converte texto com offset (ex.: 2025-10-01 07:13:41-03:00) para timestamp local sem fuso. -#}
{% macro to_local_ts(column) -%}
    timezone('{{ var("local_tz") }}', cast({{ column }} as timestamptz))
{%- endmacro %}

{#- Converte texto sem offset, gravado em UTC (CRM), para timestamp local sem fuso. -#}
{% macro utc_to_local_ts(column) -%}
    timezone('{{ var("local_tz") }}', timezone('UTC', cast({{ column }} as timestamp)))
{%- endmacro %}
