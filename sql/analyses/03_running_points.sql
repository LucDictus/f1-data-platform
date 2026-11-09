-- Championship standings after every race: cumulative points and rank per season.
WITH running AS (
    SELECT
        season,
        round,
        driver_id,
        SUM(points) OVER (PARTITION BY season, driver_id ORDER BY round) AS total_points
    FROM marts.fct_race_results
)
SELECT
    season,
    round,
    driver_id,
    total_points,
    RANK() OVER (PARTITION BY season, round ORDER BY total_points DESC) AS championship_position
FROM running
ORDER BY season, round, championship_position;
