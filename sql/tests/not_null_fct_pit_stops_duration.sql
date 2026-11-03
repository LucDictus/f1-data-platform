-- fct_pit_stops.duration_s must never be NULL.
-- Empty-string durations are dropped in staging (see stg_pitstops.sql).
SELECT season, round, driver_id, stop_number
FROM marts.fct_pit_stops
WHERE duration_s IS NULL;