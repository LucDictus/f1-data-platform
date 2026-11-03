SELECT
    COUNT(*)                                   AS total_rows,
    COUNT(*) FILTER (WHERE duration_s IS NULL) AS unparsed_durations
FROM staging.stg_pitstops;