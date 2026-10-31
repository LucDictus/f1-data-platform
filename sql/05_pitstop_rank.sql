SELECT
    round,
    race_name,
    driver_id,
    lap,
    duration_s,
    RANK() OVER (PARTITION BY round ORDER BY duration_s) AS rank_in_race
FROM pitstops_flat
WHERE duration_s < 60   -- ignore red-flag stops
QUALIFY RANK() OVER (PARTITION BY round ORDER BY duration_s) <= 3
ORDER BY round, rank_in_race;