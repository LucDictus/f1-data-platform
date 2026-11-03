-- Grain: one row per race result
CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.fct_race_results AS
SELECT
    season,
    round,
    driver_id,
    constructor_id,
    grid,
    finish_position,
    points,
    status
FROM staging.stg_results;
