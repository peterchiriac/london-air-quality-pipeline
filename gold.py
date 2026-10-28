import duckdb   

# Connect to the local DuckDB database.
con = duckdb.connect("air_quality.duckdb")

# Build the Gold daily air quality summary from Silver readings.
con.execute("""
CREATE OR REPLACE TABLE daily_pollutant_averages AS
    SELECT
    site_code,
    CAST(measurement_timestamp AS DATE) AS date,
    species_code,
    AVG(value) AS avg_concentration
FROM readings
WHERE quality_status = 'valid'
GROUP BY date, species_code, site_code
"""
)

print("Gold summary:")
print(
    con.execute("SELECT * FROM daily_pollutant_averages").fetchall()
)

con.close()