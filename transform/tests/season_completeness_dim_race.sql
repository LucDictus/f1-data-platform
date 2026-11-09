-- Every season between the first and the latest loaded season must have races in dim_race.
-- It stops at the latest season with races, not the current year, so the test still passes
-- between 1 January and the first race of a new season. Returns the missing seasons.
WITH expected AS (
    SELECT unnest(generate_series(min(season), max(season))) AS season
    FROM {{ ref('dim_race') }}
)
SELECT e.season
FROM expected AS e
LEFT JOIN {{ ref('dim_race') }} AS r
    ON e.season = r.season
WHERE r.season IS NULL
