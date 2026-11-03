SELECT f.*
FROM marts.fct_race_results AS f
         LEFT JOIN marts.dim_driver AS d ON f.driver_id = d.driver_id
WHERE d.driver_id IS NULL;