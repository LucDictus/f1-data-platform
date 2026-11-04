-- Grain: one row per race
SELECT DISTINCT
    season,
    round,
    race_name,
    race_date,
    circuit_id,
    circuit_name
FROM {{ ref('stg_results') }}
