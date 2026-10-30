import duckdb   

# Connect to the local DuckDB database.
con = duckdb.connect("air_quality.duckdb")

# Build the Gold daily air quality summary from Silver readings.
con.execute("""
CREATE OR REPLACE TABLE daily_pollutant_averages AS
    SELECT
    r.site_code,
    s.site_name,
    s.site_type,
    CAST(r.measurement_timestamp AS DATE) AS date,
    r.species_code,
    COUNT(*) FILTER (WHERE r.quality_status = 'valid') AS valid_hours,
    AVG(value) FILTER (WHERE r.quality_status = 'valid') AS avg_concentration,
    COUNT(*) FILTER (WHERE r.quality_status = 'valid') / 24.0 * 100 AS completeness_pct,
    CASE
    WHEN COUNT(*) FILTER (WHERE r.quality_status = 'valid') < 18
    THEN 'incomplete'
    ELSE 'reliable'
END AS reliability_status
FROM readings AS r
INNER JOIN sites AS s
ON r.site_code = s.site_code
WHERE r.site_code IN ('TH4', 'TH6')
GROUP BY CAST(r.measurement_timestamp AS DATE), r.species_code, r.site_code, s.site_name, s.site_type
"""
)

print("Gold summary:")
print(
    con.execute("SELECT * FROM daily_pollutant_averages LIMIT 10").fetchall()
)

con.close()