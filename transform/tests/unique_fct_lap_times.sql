SELECT season, round, driver_id, lap, COUNT(*) AS n
FROM {{ ref('fct_lap_times') }}
GROUP BY season, round, driver_id, lap
HAVING COUNT(*) > 1
