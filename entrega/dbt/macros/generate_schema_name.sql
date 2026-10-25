{#- Usa o nome da camada como schema (staging, intermediate, marts), sem prefixo do target. -#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name if custom_schema_name is not none else target.schema }}
{%- endmacro %}
