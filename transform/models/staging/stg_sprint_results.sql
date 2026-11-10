WITH races AS (
    SELECT unnest(MRData.RaceTable.Races) AS race
    FROM {{ source('jolpica', 'sprint') }}
),
sprint AS (
    SELECT
        race.season::INT   AS season,
        race.round::INT    AS round,
        unnest(race.SprintResults) AS r
    FROM races
)
SELECT
    season,
    round,
    r.Driver.driverId           AS driver_id,
    r.Constructor.constructorId AS constructor_id,
    r.grid::INT                 AS grid,
    r.position::INT             AS finish_position,
    r.points::DOUBLE            AS points,
    r.status                    AS status
FROM sprint
