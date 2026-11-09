-- Turn an API time like "1:32.456" (minutes:seconds) or "23.5" (seconds) into seconds.
{% macro to_seconds(column) -%}
    CASE
        WHEN {{ column }}::VARCHAR LIKE '%:%' THEN
            TRY_CAST(split_part({{ column }}::VARCHAR, ':', 1) AS INT) * 60
            + TRY_CAST(split_part({{ column }}::VARCHAR, ':', 2) AS DOUBLE)
        ELSE TRY_CAST({{ column }}::VARCHAR AS DOUBLE)
    END
{%- endmacro %}
