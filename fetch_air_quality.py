import requests 
from datetime import datetime, timedelta, timezone
import duckdb

# Constructing the API URL for a station
def build_readings_url(site_code, species_code, start_date, end_date):
    return f"https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode={site_code}/SpeciesCode={species_code}/StartDate={start_date}/EndDate={end_date}/Json"


# Request air quality readings from the Environmental Research Group API
def fetch_readings(url):
    r = requests.get(url)
    r.raise_for_status()
    print("HTTP status", r.status_code)
    return r


# Preserve the raw API response as the Bronze Layer
def save_raw_response(filename, r):
    with open(filename, "wb") as json_file:
        json_file.write(r.content)



# Parse the response for validation
def parse_response(response):
    data = response.json()
    return data 


def validate_readings(data, start_date, end_date):
    readings = data.get("RawAQData").get("Data")
    timestamps = []
    
    if not readings:
        print("No readings returned by the API. Validation cannot continue.")

        return
    # Extract and parse timestamps from the API readings for validation.
    for reading in readings:
        s = reading["@MeasurementDateGMT"]
        v = reading["@Value"]
        dt = datetime.fromisoformat(s) 
        timestamps.append(dt)
        if not v:
            print("Missing pollutant value at:", dt) 
        else: 
            v = float(v)
            if v < 0:
                print(f"Negative value: {dt}: {v}")


    timestamps.sort()

    expected_timestamps = []

    start = datetime.fromisoformat(f"{start_date}T00:00")
    end = datetime.fromisoformat(f"{end_date}T00:00")
    duration = int((end - start).total_seconds() // 3600)

    # Generate expected hourly timestamps for the requested date range to identify missing readings.
    for i in range(duration):
        minutes_to_add = i * 60
        expected_timestamp = start + timedelta(minutes=minutes_to_add)
        expected_timestamps.append(expected_timestamp)

    missing_timestamps = set(expected_timestamps) - set(timestamps)
    if missing_timestamps:
        print(f"Missing {len(missing_timestamps)} hourly readings")
        print(missing_timestamps)

    print("Actual timestamps:", len(timestamps))
    print("Expected timestamps:", len(expected_timestamps))

def get_start_date(site_code, species_code):
        con = duckdb.connect("air_quality.duckdb")
        query = """
        SELECT
        MAX(measurement_timestamp)
        FROM readings
        WHERE site_code = ?
        AND species_code = ?
    """
        result = con.execute(query, [site_code, species_code]).fetchone()
        last_timestamp = result[0]
        con.close()
        if last_timestamp is None:
            return start_date
        else:
            new_start = last_timestamp - timedelta(days=3)
        new_start = new_start.strftime("%Y-%m-%d")
            
        return new_start
    
site_code = "BQ7"
species_codes = ["NO2", "O3"]
start_date = "2025-06-01"
end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Main execution loop: fetch, save and validate readings for each pollutant.
for species_code in species_codes:
    fetch_start_date = get_start_date(site_code, species_code)
    print(f"Fetching from {fetch_start_date} to {end_date}")
    print(f"\nFetching {species_code} for station {site_code}")
    url = build_readings_url(site_code, species_code, fetch_start_date, end_date)
    response = fetch_readings(url)

    filename = f"bronze/readings_{site_code}_{species_code}_{fetch_start_date}_{end_date}.json"
    save_raw_response(filename, response)

    data = parse_response(response)
    validate_readings(data, fetch_start_date, end_date)



  







