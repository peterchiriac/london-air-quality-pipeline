import requests 
from datetime import datetime, timedelta

# Constructing the API URL for a station
def build_readings_url(site_code, species_code, start_date, end_date):
    return f"https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode={site_code}/SpeciesCode={species_code}/StartDate={start_date}/EndDate={end_date}/Json"

site_code = "BQ7"
species_code = "NO2"
start_date = "2025-06-01"
end_date = "2025-06-08"

url = build_readings_url(site_code, species_code, start_date, end_date)

# Request air quality readings from the Environmental Research Group API
def fetch_readings(url):
    r = requests.get(url)
    r.raise_for_status()
    print("HTTP status", r.status_code)
    return r

response = fetch_readings(url)
print(response)

filename = f"bronze/readings_{site_code}_{species_code}_{start_date}_{end_date}.json"

# Preserve the raw API response as the Bronze Layer
def save_raw_response(filename, r):
    with open(filename, "wb") as json_file:
        json_file.write(r.content)

save_raw_response(filename, response)

# Parse the response for validation

def parse_response(response):
    data = response.json()
    return data 

data = parse_response(response)

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
    
      
validate_readings(data, start_date, end_date)
