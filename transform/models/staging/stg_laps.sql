WITH races AS (
    SELECT unnest(MRData.RaceTable.Races) AS race
    FROM {{ source('jolpica', 'laps') }}
),
     laps AS (
         SELECT
             race.season::INT AS season,
             race.round::INT  AS round,
             unnest(race.Laps) AS l
         FROM races
     ),
     timings AS (
         SELECT
             season,
             round,
             l.number::INT AS lap,
             unnest(l.Timings) AS t
         FROM laps
     )
SELECT
    season,
    round,
    lap,
    t.driverId::VARCHAR AS driver_id,
    t.position::INT     AS position,
    t.time::VARCHAR     AS lap_time_raw,
    CASE
        WHEN t.time::VARCHAR LIKE '%:%' THEN
            TRY_CAST(split_part(t.time::VARCHAR, ':', 1) AS INT) * 60
            + TRY_CAST(split_part(t.time::VARCHAR, ':', 2) AS DOUBLE)
        ELSE TRY_CAST(t.time::VARCHAR AS DOUBLE)
END AS lap_time_s
FROM timings
