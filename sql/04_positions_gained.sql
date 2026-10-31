SELECT
    round,
    race_name,
    driver_id,
    grid,
    finish_position,
    grid - finish_position AS positions_gained
FROM results_flat
WHERE grid > 0   -- grid 0 means a pit-lane start, which would distort the numbers
QUALIFY RANK() OVER (PARTITION BY round ORDER BY grid - finish_position DESC) = 1
ORDER BY round;