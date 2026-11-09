-- The driver who gained the most places from grid to finish in every race.
SELECT
    f.season,
    f.round,
    r.race_name,
    f.driver_id,
    f.grid,
    f.finish_position,
    f.grid - f.finish_position AS positions_gained
FROM marts.fct_race_results AS f
JOIN marts.dim_race AS r
    ON  f.season = r.season
    AND f.round  = r.round
WHERE f.grid > 0   -- grid 0 means a pit-lane start, which would distort the numbers
QUALIFY RANK() OVER (PARTITION BY f.season, f.round ORDER BY f.grid - f.finish_position DESC) = 1
ORDER BY f.season, f.round;
