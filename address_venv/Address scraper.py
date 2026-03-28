import pandas as pd
import requests
import time
import openpyxl 

# Query all hospitals in Lagos State
query = """
[out:json];
area["name"="Lagos"]["boundary"="administrative"]->.searchArea;
node["amenity"="hospital"](area.searchArea);
out body;
"""

response = requests.get(
    "https://overpass-api.de/api/interpreter",
    params={"data": query}
)

if response.status_code != 200:
    print(f"Error {response.status_code} from Overpass API: {response.text}")
    exit(1)

try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print(f"Failed to parse JSON response: {response.text}")
    exit(1)

hospitals = data.get("elements", [])
print(f"Found {len(hospitals)} hospitals from OpenStreetMap. Processing addresses...")

results = []

for i, element in enumerate(hospitals, 1):
    tags = element.get("tags", {})
    name = tags.get("name", "Unknown")
    lat = element.get("lat")
    lon = element.get("lon")
    
    # Try to build address from tags
    address_parts = []
    if "addr:housenumber" in tags:
        address_parts.append(tags["addr:housenumber"])
    if "addr:street" in tags:
        address_parts.append(tags["addr:street"])
    if "addr:city" in tags:
        address_parts.append(tags["addr:city"])
        
    full_address = tags.get("addr:full")
    
    if full_address:
        address = full_address
    elif address_parts:
        address = ", ".join(address_parts)
    else:
        address = None

    if not address and lat and lon:
        # If no address tag was found, reverse geocode the coordinates
        print(f"[{i}/{len(hospitals)}] Address missing. Reverse geocoding for: {name}...")
        try:
            # Nominatim Public API Usage Policy strictly limits to max 1 request per second
            time.sleep(1.2)  
            rev_res = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json",
                headers={'User-Agent': 'HospitalAddressScraper/1.0 (local)'}
            )
            if rev_res.status_code == 200:
                address = rev_res.json().get("display_name", "Not available")
            else:
                address = "Not available"
        except Exception:
            address = "Not available"
    elif not address:
        address = "Not available"

    results.append({
        "Hospital": name,
        "Address": address,
        "Latitude": lat,
        "Longitude": lon
    })

df = pd.DataFrame(results)
df.to_excel("hospitals_lagos.xlsx", index=False)
print("Finished! Saved all data to hospitals_lagos.xlsx")