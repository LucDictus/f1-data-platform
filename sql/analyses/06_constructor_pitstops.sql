-- “Fastest average pit stop per constructor” needs a join, because pit stops only contain driver_id. Join pitstops_flat to results_flat on round and driver_id to get the constructor, then GROUP BY constructor_id. This is your first taste of how a fact table and a dimension relate, so try it as sql/06_constructor_pitstops.sql before looking for help.
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