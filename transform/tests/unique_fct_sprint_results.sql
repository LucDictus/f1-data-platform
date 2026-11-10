-- fct_sprint_results must have one row per driver per sprint
SELECT season, round, driver_id, COUNT(*) AS n
FROM {{ ref('fct_sprint_results') }}
GROUP BY season, round, driver_id
HAVING COUNT(*) > 1
