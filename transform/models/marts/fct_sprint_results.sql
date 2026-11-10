-- Grain: one row per driver per sprint
SELECT
    season,
    round,
    driver_id,
    constructor_id,
    grid,
    finish_position,
    points,
    status
FROM {{ ref('stg_sprint_results') }}
