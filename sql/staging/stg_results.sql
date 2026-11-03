CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE VIEW staging.stg_results AS
WITH races AS (
    SELECT unnest(MRData.RaceTable.Races) AS race
    FROM read_json_auto('data/raw/results/season=2024/data.json')
),
results AS (
    SELECT
        race.season::INT   AS season,
        race.round::INT    AS round,
        race.raceName      AS race_name,
        race.date::DATE    AS race_date,
        race.Circuit.circuitId AS circuit_id,
        race.Circuit.circuitName AS circuit_name,
        unnest(race.Results) AS r
    FROM races
)
SELECT
    season,
    round,
    race_name,
    race_date,
    circuit_id,
    circuit_name,
    r.Driver.driverId           AS driver_id,
    r.Driver.code               AS driver_code,
    r.Driver.nationality        AS driver_nationality,
    r.Driver.givenName          AS driver_given_name,
    r.Driver.familyName         AS driver_family_name,
    r.Constructor.constructorId AS constructor_id,
    r.Constructor.name AS constructor_name,
    r.Constructor.nationality AS constructor_nationality,
    r.grid::INT                 AS grid,
    r.position::INT             AS finish_position,
    r.points::DOUBLE            AS points,
    r.status                    AS status
FROM results;

