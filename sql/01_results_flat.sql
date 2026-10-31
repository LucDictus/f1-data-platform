CREATE OR REPLACE VIEW results_flat AS
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
        unnest(race.Results) AS r
    FROM races
)
SELECT
    season,
    round,
    race_name,
    race_date,
    r.Driver.driverId           AS driver_id,
    r.Constructor.constructorId AS constructor_id,
    r.grid::INT                 AS grid,
    r.position::INT             AS finish_position,
    r.points::DOUBLE            AS points,
    r.status                    AS status
FROM results;

SELECT * FROM results_flat ORDER BY round, finish_position;

-- 479 rows (50 shown)  
