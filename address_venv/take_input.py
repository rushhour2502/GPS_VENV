import pandas as pd
import requests
import time

def search_hospitals(hospital_list=None):
    """
    Search for a list of hospitals using the Nominatim API and return a DataFrame.
    If hospital_list is not provided, it will prompt the user to input them.
    """
    if hospital_list is None:
        print("Enter a list of hospitals you want to search for, separated by commas.")
        print("For example: Lagoon Hospital, Eko Hospital, Reddington Hospital")
        user_input = input("\nHospitals: ")

        if not user_input.strip():
            print("No hospitals provided. Exiting.")
            return None
        
        # Parse the input into a clean list
        hospital_names = [name.strip() for name in user_input.split(",") if name.strip()]
    else:
        # User provided the list directly from Python
        if isinstance(hospital_list, str):
            # If they passed a single string by accident
            hospital_names = [hospital_list]
        else:
            hospital_names = hospital_list

    print(f"\nSearching Nominatim API for {len(hospital_names)} hospital(s)...\n")

    results = []
    HEADERS = {'User-Agent': 'HospitalAddressScraper/1.0 (local)'}

    for i, name in enumerate(hospital_names, 1):
        print(f"[{i}/{len(hospital_names)}] Searching for: {name}...")
        
        # We append "Lagos" to the query to restrict results geographically
        query_str = f"{name}, Lagos"
        
        try:
            # Nominatim Public API Usage Policy strictly requires max 1 request per second
            time.sleep(1.2)  
            res = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query_str,
                    "format": "json",
                    "limit": 1
                },
                headers=HEADERS
            )
            
            if res.status_code == 200:
                data = res.json()
                if data:
                    # Get the top geographical match
                    top_match = data[0]
                    lat = top_match.get("lat")
                    lon = top_match.get("lon")
                    
                    # Nominatim provides a full formatted address in 'display_name'
                    address = top_match.get("display_name", "Not available")
                    
                    results.append({
                        "Hospital": name,
                        "Address": address,
                        "Latitude": lat,
                        "Longitude": lon
                    })
                else:
                    print(f"  -> No results found for '{name}' in Lagos.")
                    results.append({
                        "Hospital": name,
                        "Address": "Not found",
                        "Latitude": "N/A",
                        "Longitude": "N/A"
                    })
            else:
                print(f"  -> API Error HTTP {res.status_code} for '{name}'")
                
        except Exception as e:
            print(f"  -> Connection error for '{name}': {e}")
            results.append({
                "Hospital": name,
                "Address": "Error",
                "Latitude": "N/A",
                "Longitude": "N/A"
            })

    # ==========================================
    # 3. EXPORT TO EXCEL
    # ==========================================
    if results:
        df = pd.DataFrame(results)
        output_filename = "custom_hospitals_lagos.xlsx"
        df.to_excel(output_filename, index=False)
        print(f"\nFinished! Saved all data to {output_filename}")
        return df
    else:
        print("\nNo hospitals found matching your input.")
        return None

# Allow the script to run standalone in the terminal
if __name__ == "__main__":
    search_hospitals()
