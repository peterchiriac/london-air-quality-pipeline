import requests 
from datetime import datetime, timedelta

# Constructing the API URL for a station
def build_readings_url(site_code, species_code, start_date, end_date):
    return f"https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode={site_code}/SpeciesCode={species_code}/StartDate={start_date}/EndDate={end_date}/Json"

site_code = "BQ7"
species_code = "NO2"
start_date = "2025-06-01"
end_date = "2025-06-02"

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
    #
    if not readings:
        print("No readings returned by the API. Validation cannot continue.")

        return

    for reading in readings:
        s = reading["@MeasurementDateGMT"]
        dt = datetime.fromisoformat(s) 
        timestamps.append(dt)

    timestamps.sort()

    expected_timestamps = []

    start = datetime.fromisoformat(f"{start_date}T00:00")
    end = datetime.fromisoformat(f"{end_date}T00:00")
    duration = int((end - start).total_seconds() // 3600)

    for i in range(duration):
        minutes_to_add = i * 60
        expected_timestamp = start + timedelta(minutes=minutes_to_add)
        expected_timestamps.append(expected_timestamp)

    missing_timestamps = set(expected_timestamps) - set(timestamps)

    print(len(timestamps))
    print(len(expected_timestamps))
    print((missing_timestamps))

   

   
validate_readings(data, start_date, end_date)
