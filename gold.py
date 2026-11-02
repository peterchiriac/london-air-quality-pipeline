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

print("\n" + "=" * 80)
print("GOLD LAYER — DAILY AIR QUALITY SUMMARY")
print("=" * 80)

print(f"{'Date':<12} {'Site':<8} {'Pollutant':<12} {'Average':<12} {'Coverage':<12} {'Status'}")
print("-" * 80)

rows = con.execute("SELECT * FROM daily_pollutant_averages ORDER BY date DESC LIMIT 10").fetchall()
for row in rows:
    date = row[3]
    site = row[0]
    pollutant = row[4]
    average = row[6]
    completeness = row[7]
    status = row[8]
    if average is None:
        average = "N/A"
    else:
        average = (round(average, 2))
    print(f"{date!s:<12} {site:<8} {pollutant:<12} {average!s:<12} {completeness:<12.1f} {status}")

con.close()
