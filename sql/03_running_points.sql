WITH running AS (
    SELECT
        round,
        driver_id,
        SUM(points) OVER (PARTITION BY driver_id ORDER BY round) AS total_points
    FROM results_flat
)
SELECT
    round,
    driver_id,
    total_points,
    RANK() OVER (PARTITION BY round ORDER BY total_points DESC) AS championship_position
FROM running
ORDER BY round, championship_position;