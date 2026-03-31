import pandas as pd
import time
import re
import math
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

print("Fetching D1 arenas list from Wikipedia...")
url = "https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_basketball_arenas"
tables = pd.read_html(url)

# Find the correct table containing the arenas
df = None
for table in tables:
    if 'Arena' in table.columns and 'Capacity' in table.columns and 'Team' in table.columns:
        df = table
        break

if df is None:
    print("Could not find the arenas table on Wikipedia!")
    exit(1)

# Clean up column names and data
df.columns = [col.replace(' ', '_') for col in df.columns]

# Ensure we have the basic columns
print(f"Loaded {len(df)} initial rows from Wikipedia.")

# Prepare the final dataframe structure
# School,Mascot,Arena,Hex,Hex2,Lat,Lon,Furthest_Round,Capacity,Avg_Attendance
output_data = []

geolocator = Nominatim(user_agent="d1_basketball_geocoder_2026")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

# A small dictionary for vivid default colors
color_pairs = [
    ("#CC0000", "#000000"), ("#0033A0", "#FFFFFF"), ("#00274C", "#FFCB05"),
    ("#C8102E", "#F1BE48"), ("#E84A27", "#13294B"), ("#C5050C", "#FFFFFF"),
    ("#FF8200", "#FFFFFF"), ("#003087", "#FFFFFF"), ("#18453B", "#FFFFFF"),
    ("#4D1979", "#FFFFFF"), ("#FFCD00", "#000000"), ("#000000", "#BA9B37")
]

print("Geocoding arenas (this will take ~6-7 minutes to respect free API rate limits)...")

success = 0
failed = 0

for idx, row in df.iterrows():
    if idx % 50 == 0:
        print(f"Processed {idx} / {len(df)} teams...")
        
    school_team = str(row['Team']).split('[')[0].strip()
    
    # Try to extract the mascot by assuming the last word is the mascot
    # e.g., "Florida Gators" -> "Gators", "Florida"
    parts = school_team.split(' ')
    if len(parts) > 1:
        mascot = parts[-1]
        school = ' '.join(parts[:-1])
    else:
        school = school_team
        mascot = "Unlisted"
        
    arena = str(row['Arena']).split('[')[0].strip()
    city = str(row.get('City', '')).split('[')[0].strip()
    state = str(row.get('State', '')).split('[')[0].strip()
    
    # Fix capacity parsing
    cap_raw = str(row['Capacity']).replace(',', '').split('[')[0].strip()
    try:
        capacity = int(cap_raw)
    except:
        capacity = 5000 # default
        
    # Geocoding
    query = f"{arena}, {city}, {state}"
    location = geocode(query)
    
    # Fallback just City, State if the arena is not found
    if location is None:
        location = geocode(f"{school} University, {city}, {state}")
    
    if location is None:
        location = geocode(f"{city}, {state}")

    if location:
        lat = location.latitude
        lon = location.longitude
        success += 1
    else:
        # Extreme fallback to generic center of US if totally unfound
        lat, lon = 39.8283, -98.5795
        failed += 1
        
    # Assign colors round-robin
    c1, c2 = color_pairs[idx % len(color_pairs)]
    
    output_data.append({
        'School': school,
        'Mascot': mascot,
        'Arena': arena,
        'Hex': c1,
        'Hex2': c2,
        'Lat': round(lat, 4),
        'Lon': round(lon, 4),
        'Furthest_Round': 362,
        'Capacity': capacity,
        'Avg_Attendance': capacity  # default assumption
    })

print(f"Geocoding complete! Success: {success}, Failed/Defaults: {failed}")

final_df = pd.DataFrame(output_data)
final_df.to_csv("ncaa_d1_teams_initial.csv", index=False)
print("Saved all teams to ncaa_d1_teams_initial.csv!")
