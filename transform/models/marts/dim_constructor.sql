-- Grain: one row per constructor
SELECT DISTINCT
    c.constructor_id,
    c.constructor_name,
    c.constructor_nationality,
    t.team_lineage
FROM {{ ref('stg_results') }} AS c
LEFT JOIN {{ ref('team_lineage') }} AS t
ON c.constructor_id = t.constructor_id
