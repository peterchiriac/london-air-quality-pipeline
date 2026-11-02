--- Query 1 — Before and after incremental ingestion

SELECT
    site_code,
    species_code,
    COUNT(*) AS total_readings,
    MAX(measurement_timestamp) AS latest_reading
FROM readings
GROUP BY
    site_code,
    species_code
ORDER BY
    site_code,
    species_code;


--- Query 2 — Verify no duplicate observations

SELECT
    site_code,
    species_code,
    measurement_timestamp,
    COUNT(*) AS occurrences
FROM readings
GROUP BY
    site_code,
    species_code,
    measurement_timestamp
HAVING COUNT(*) > 1;



--- Query 3 — Inspect quality classifications

SELECT
    site_code,
    species_code,
    quality_status,
    COUNT(*) AS observations
FROM readings
GROUP BY
    site_code,
    species_code,
    quality_status
ORDER BY
    site_code,
    species_code,
    quality_status;