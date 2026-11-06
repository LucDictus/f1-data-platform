-- Grain: one row per season, round, driver and lap
{{ config(
    materialized='incremental',
    unique_key=['season', 'round', 'driver_id', 'lap']
) }}

SELECT
    season,
    round,
    driver_id,
    lap,
    position,
    lap_time_s
FROM {{ ref('stg_laps') }}
{% if is_incremental() %}
    WHERE (season, round) NOT IN (SELECT DISTINCT season, round FROM {{ this }})
{% endif %}
