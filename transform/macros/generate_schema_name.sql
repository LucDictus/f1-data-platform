-- Use +schema as-is ("marts") instead of dbt's default "<target schema>_marts" ("main_marts").
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name if custom_schema_name else target.schema }}
{%- endmacro %}
