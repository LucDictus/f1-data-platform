-- Average pit stop time per team over all seasons, without red-flag stops.
SELECT
    f.constructor_id,
    d.constructor_name,
    ROUND(AVG(f.duration_s), 2)   AS avg_pit_stop_s,
    COUNT(*)                    AS stops
FROM marts.fct_pit_stops AS f
JOIN marts.dim_constructor AS d
    ON f.constructor_id = d.constructor_id
WHERE NOT f.is_long_stop
GROUP BY f.constructor_id, d.constructor_name
ORDER BY avg_pit_stop_s;