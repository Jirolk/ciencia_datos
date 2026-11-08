{#- Usa el nombre de esquema configurado tal cual (staging, intermediate, marts)
    en lugar del comportamiento por defecto de dbt (main_staging, ...). -#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
