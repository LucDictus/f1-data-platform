CREATE OR REPLACE VIEW pitstops_flat AS
WITH races AS (
    SELECT unnest(MRData.RaceTable.Races) AS race
    FROM read_json_auto('data/raw/pitstops/season=2024/round=*/data.json')
),
stops AS (
    SELECT
        race.season::INT AS season,
        race.round::INT  AS round,
        race.raceName    AS race_name,
        unnest(race.PitStops) AS p
    FROM races
)
SELECT
    season,
    round,
    race_name,
    p.driverId::VARCHAR AS driver_id,
    p.stop::INT         AS stop_number,
    p.lap::INT          AS lap,
    p.time::TIME        AS local_time,
    p.duration::VARCHAR AS duration_raw,
    CASE
        WHEN p.duration::VARCHAR LIKE '%:%' THEN
            TRY_CAST(split_part(p.duration::VARCHAR, ':', 1) AS INT) * 60
            + TRY_CAST(split_part(p.duration::VARCHAR, ':', 2) AS DOUBLE)
        ELSE TRY_CAST(p.duration::VARCHAR AS DOUBLE)
    END AS duration_s
FROM stops;

SELECT * FROM pitstops_flat ORDER BY duration_s DESC LIMIT 20;