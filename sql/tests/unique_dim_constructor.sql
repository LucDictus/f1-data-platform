-- dim_constructor must have one row per constructor
SELECT constructor_id, COUNT(*) AS n
FROM marts.dim_constructor
GROUP BY constructor_id
HAVING COUNT(*) > 1;