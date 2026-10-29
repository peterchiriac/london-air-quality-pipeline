import duckdb
import json 
from datetime import datetime 
from pathlib import Path


# Connect to DuckDB and create the Silver readings table if it doesn't exist.
# The composite primary key uniquely identifies each station-pollutant-hour combination.
con = duckdb.connect("air_quality.duckdb")

con.execute("""CREATE TABLE IF NOT EXISTS readings(
    site_code VARCHAR, 
    species_code VARCHAR,
    measurement_timestamp TIMESTAMP,
    value DOUBLE,
    quality_status VARCHAR,
    PRIMARY KEY(site_code, species_code, measurement_timestamp)
    )
""")

# Use parameterised SQL to insert readings.
# Update existing records when incoming measurements are valid
insert_sql = """
INSERT INTO readings (
    site_code,
    species_code,
    measurement_timestamp,
    value,
    quality_status
)
VALUES ( 
    $site_code,
    $species_code,
    $measurement_timestamp,
    $value,
    $quality_status
    )
    ON CONFLICT (site_code, species_code, measurement_timestamp)
    DO UPDATE SET 
        value = EXCLUDED.value,
        quality_status = EXCLUDED.quality_status
        WHERE EXCLUDED.quality_status = 'valid'
"""
# Process every saved Bronze readings file.
# Extract station and pollutant identifiers from the filename.
for filename in sorted(
    Path("bronze").glob("readings_*.json"),
    key=lambda p: p.stat().st_mtime
):
    parts = filename.stem.split("_")
    site_code = parts[1]
    species_code = parts[2]

    # Read the preserved Bronze API response rather than requesting the data again.
    with open(filename, "r") as json_file:
        data = json.load(json_file)

    # Extract hourly observations from the nested API response.
    readings = data.get("RawAQData").get("Data")
    print(len(readings))

    # Convert timestamps and pollutant values into appropriate Python types.
    # Preserve missing and negative measurements, assigning quality flags.
    for reading in readings:
        t = reading["@MeasurementDateGMT"]
        v = reading["@Value"]
        dt = datetime.fromisoformat(t)
        if not v:
            value = None 
            quality_status = "missing"
        else:
            value = float(v)

            if value < 0:
                quality_status = "negative"
            else:
                quality_status = "valid"

        # Insert the transformed reading with its station and pollutant identifiers.
        params = {
            "site_code": site_code,
            "species_code": species_code,
            "measurement_timestamp": dt,
            "value": value,
            "quality_status": quality_status
        }
        con.execute(insert_sql, params)

con.close()


