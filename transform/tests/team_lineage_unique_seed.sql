SELECT constructor_id, COUNT(*) AS n
FROM {{ ref('team_lineage') }}
GROUP BY constructor_id
HAVING COUNT(*) > 1
