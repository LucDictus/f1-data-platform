-- Grain: one row per pit stop
CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.fct_pit_stops AS
SELECT
    p.season,
    p.round,
    p.driver_id,
    r.constructor_id,
    p.stop_number,
    p.lap,
    p.duration_s
FROM staging.stg_pitstops AS p
LEFT JOIN staging.stg_results AS r
    ON  p.season    = r.season
    AND p.round     = r.round
    AND p.driver_id = r.driver_id