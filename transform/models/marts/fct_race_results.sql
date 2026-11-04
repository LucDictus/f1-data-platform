-- Grain: one row per race result
SELECT
    season,
    round,
    driver_id,
    constructor_id,
    grid,
    finish_position,
    points,
    status
FROM {{ ref('stg_results') }}
