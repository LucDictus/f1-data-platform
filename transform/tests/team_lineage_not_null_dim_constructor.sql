-- Every constructor must have a team lineage. A new constructor_id means the seed needs a row.
SELECT constructor_id, constructor_name
FROM {{ ref('dim_constructor') }}
WHERE team_lineage IS NULL
