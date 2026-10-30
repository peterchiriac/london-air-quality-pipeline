import duckdb

con = duckdb.connect("air_quality.duckdb")

# Create readings table
con.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        site_code VARCHAR,
        species_code VARCHAR,
        measurement_timestamp TIMESTAMP,
        value DOUBLE,
        quality_status VARCHAR,
        PRIMARY KEY (site_code, species_code, measurement_timestamp)
    )
""")

# Create sites table
con.execute("""
    CREATE TABLE IF NOT EXISTS sites (
        site_code VARCHAR,
        site_name VARCHAR,
        site_type VARCHAR,
        local_authority VARCHAR,
        latitude DOUBLE,
        longitude DOUBLE,
        PRIMARY KEY (site_code)
    )
""")

con.close()

print("Database initialized successfully.")