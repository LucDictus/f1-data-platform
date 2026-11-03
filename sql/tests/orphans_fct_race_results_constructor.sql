SELECT f.*
FROM marts.fct_race_results AS f
         LEFT JOIN marts.dim_constructor AS d ON f.constructor_id = d.constructor_id
WHERE d.constructor_id IS NULL;