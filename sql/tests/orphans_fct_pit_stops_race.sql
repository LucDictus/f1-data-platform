SELECT f.*
FROM marts.fct_pit_stops AS f
         LEFT JOIN marts.dim_race AS d
                   ON  f.season = d.season
                       AND f.round  = d.round
WHERE d.season IS NULL;