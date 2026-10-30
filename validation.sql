SELECT
    COUNT(*) AS total_sites,
    COUNT(DISTINCT site_code) AS unique_sites,
    COUNT(*) FILTER (WHERE latitude IS NULL OR longitude IS NULL) AS sites_missing_coordinates
FROM sites;

SELECT
    s.site_code,
    s.site_name,
    s.site_type,
    r.species_code
FROM readings AS r
INNER JOIN sites AS s
ON r.site_code = s.site_code
LIMIT 10;

SELECT
    s.site_code,
    s.site_name,
    s.site_type,
    r.species_code
FROM readings AS r
LEFT JOIN sites AS s
ON r.site_code = s.site_code
WHERE s.site_code IS NULL;

SELECT species_code, species_name, unit
FROM pollutants
ORDER BY species_code;


SELECT site_code, site_name, site_type
FROM sites
WHERE site_type = 'Roadside'
ORDER BY site_name;

SELECT
    site_code,
    species_code,
    COUNT(*) AS total_readings,
    COUNT(*) FILTER (WHERE quality_status = 'valid') AS valid_readings,
    COUNT(*) FILTER (WHERE value IS NULL) AS missing_values,
    COUNT(*) FILTER (WHERE value < 0) AS negative_values,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE quality_status = 'valid')
        / NULLIF(COUNT(*), 0),
        2
    ) AS valid_percentage
FROM readings
WHERE site_code IN ('TH4', 'TH6')
  AND species_code IN ('NO2', 'O3')
GROUP BY site_code, species_code
ORDER BY site_code, species_code;

SELECT *
FROM daily_pollutant_averages
WHERE site_code IN ('TH4', 'TH6')
  AND date BETWEEN '2026-06-01' AND '2026-06-10'
ORDER BY date, site_code, species_code;