WITH races AS (
    SELECT unnest(MRData.RaceTable.Races) AS race
    FROM {{ source('jolpica', 'pitstops') }}
),
stops AS (
    SELECT
        race.season::INT AS season,
        race.round::INT  AS round,
        race.raceName    AS race_name,
        race.Circuit.circuitId AS circuit_id,
        unnest(race.PitStops) AS p
    FROM races
)
SELECT
    season,
    round,
    race_name,
    circuit_id,
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
FROM stops
-- Dropped: one raw row has an empty duration. A pit stop without a time is
-- useless for duration analysis, and dropping it keeps duration_s NOT NULL
-- downstream. Side effect: a gap in stop_number for that driver.
WHERE p.duration::VARCHAR != ''
