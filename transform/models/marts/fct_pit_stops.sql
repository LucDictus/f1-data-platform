-- Grain: one row per pit stop
SELECT
    p.season,
    p.round,
    p.driver_id,
    r.constructor_id,
    p.stop_number,
    p.lap,
    p.duration_s
FROM {{ ref('stg_pitstops') }} AS p
LEFT JOIN {{ ref('stg_results') }} AS r
    ON  p.season    = r.season
    AND p.round     = r.round
    AND p.driver_id = r.driver_id
