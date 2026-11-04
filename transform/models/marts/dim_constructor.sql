-- Grain: one row per constructor
SELECT DISTINCT
    constructor_id,
    constructor_name,
    constructor_nationality
FROM {{ ref('stg_results') }}
