-- Every season from 2018 to the current year must have at least one race in dim_race.
-- Returns the missing seasons; any row = failure.
WITH expected AS (
    SELECT unnest(generate_series(2018, year(current_date))) AS season
)
SELECT e.season
FROM expected AS e
         LEFT JOIN {{ ref('dim_race') }} AS r
ON e.season = r.season
WHERE r.season IS NULL
