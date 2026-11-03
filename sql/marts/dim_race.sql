-- Grain: one row per race
CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.dim_race AS
SELECT DISTINCT
    season,
    round,
    race_name,
    race_date,
    circuit_id,
    circuit_name
FROM staging.stg_results;
