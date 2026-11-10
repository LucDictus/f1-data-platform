-- Reconciliation: Verstappen's 2024 total (GP + sprints) must match the official standings, 437 points.
WITH all_points AS (
    SELECT season, driver_id, points
    FROM {{ ref('fct_race_results') }}
    WHERE season = 2024
      AND driver_id = 'max_verstappen'

    UNION ALL

    SELECT season, driver_id, points
    FROM {{ ref('fct_sprint_results') }}
    WHERE season = 2024
      AND driver_id = 'max_verstappen'
)

SELECT SUM(points) AS total_points
FROM all_points
HAVING COALESCE(SUM(points), 0) != 437
