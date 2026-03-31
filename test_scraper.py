import requests
import re
import json

def fetch_colors():
    url = "https://teamcolorcodes.com/ncaa-color-codes/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        html = requests.get(url, headers=headers, timeout=10).text
    except Exception as e:
        print("Failed to fetch:", e)
        return
        
    print("Fetched HTML of length:", len(html))
    
    # teamcolorcodes usually puts background-color:#123456 inside the style tags of the team buttons
    # Format: <a class="team-button" style="background-color:#123456; color:#ffffff;" href="link">Team Name</a>
    # Or in the big table of NCAA teams.
    
    pattern = r'<a class=\"team-button\" style=\"background-color:(#[a-fA-F0-9]{6});.*?>([^<]+)</a>'
    matches = re.findall(pattern, html)
    
    if matches:
        print(f"Found {len(matches)} teams via standard team-button class.")
        for b in matches[:5]: print(b)
    else:
        print("Standard pattern failed. Trying to find team links...")
        links = re.findall(r'<a href=\"https://teamcolorcodes.com/([^\"]+?)-color-codes/\">(.*?)</a>', html)
        print(f"Found {len(links)} links. Example:", links[:5])

if __name__ == '__main__':
    fetch_colors()
