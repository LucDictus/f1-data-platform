-- The three fastest pit stops in every race.
SELECT
    p.season,
    p.round,
    r.race_name,
    p.driver_id,
    p.lap,
    p.duration_s,
    RANK() OVER (PARTITION BY p.season, p.round ORDER BY p.duration_s) AS rank_in_race
FROM marts.fct_pit_stops AS p
JOIN marts.dim_race AS r
    ON  p.season = r.season
    AND p.round  = r.round
WHERE NOT p.is_long_stop
QUALIFY rank_in_race <= 3
ORDER BY p.season, p.round, rank_in_race;
