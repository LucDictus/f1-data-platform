SELECT f.*
FROM {{ ref('fct_pit_stops') }} AS f
         LEFT JOIN {{ ref('dim_race') }} AS d
                   ON  f.season = d.season
                       AND f.round  = d.round
WHERE d.season IS NULL
