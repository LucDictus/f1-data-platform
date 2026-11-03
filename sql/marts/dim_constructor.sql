-- Grain: one row per constructor
CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.dim_constructor AS
SELECT DISTINCT
    constructor_id,
    constructor_name,
    constructor_nationality
FROM staging.stg_results;