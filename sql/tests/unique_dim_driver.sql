-- dim_driver must have one row per driver
SELECT driver_id, COUNT(*) AS n
FROM marts.dim_driver
GROUP BY driver_id
HAVING COUNT(*) > 1;