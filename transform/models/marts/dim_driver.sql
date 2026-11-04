-- Grain: one row per driver
SELECT DISTINCT
    driver_id,
    driver_code,
    driver_nationality,
    driver_given_name,
    driver_family_name
FROM {{ ref('stg_results') }}
