-- fct_pit_stops must have one row per pit stop
SELECT season, round, driver_id, stop_number, COUNT(*) AS n
FROM marts.fct_pit_stops
GROUP BY season, round, driver_id, stop_number
HAVING COUNT(*) > 1;