-- fct_race_results must have one row per driver per race
SELECT season, round, driver_id, COUNT(*) AS n
FROM {{ ref('fct_race_results') }}
GROUP BY season, round, driver_id
HAVING COUNT(*) > 1
