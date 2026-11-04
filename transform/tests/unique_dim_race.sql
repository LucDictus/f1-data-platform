-- dim_race must have one row per race
SELECT season, round, COUNT(*) AS n
FROM {{ ref('dim_race') }}
GROUP BY season, round
HAVING COUNT(*) > 1
