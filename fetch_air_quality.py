import requests 

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


