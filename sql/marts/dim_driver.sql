-- Grain: one row per driver
CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.dim_driver AS
SELECT DISTINCT
    driver_id,
    driver_code,
    driver_nationality,
    driver_given_name,
    driver_family_name
FROM staging.stg_results;