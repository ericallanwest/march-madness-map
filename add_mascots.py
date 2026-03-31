import pandas as pd
import requests
import io
import re

def fuzzy_match(school_name, wiki_df):
    clean_school = school_name.replace('University', '').replace('College', '').strip().lower()
    
    # 1. Exact Match on Common Name
    exact_common = wiki_df[wiki_df['Common name'].str.lower() == school_name.lower()]
    if len(exact_common) == 1: return exact_common.iloc[0]['Nickname']
    
    # 2. Exact Match on School
    exact_school = wiki_df[wiki_df['School'].str.lower() == school_name.lower()]
    if len(exact_school) == 1: return exact_school.iloc[0]['Nickname']
    
    # 3. Contains match
    for _, row in wiki_df.iterrows():
        c_name = str(row['Common name']).lower()
        s_name = str(row['School']).lower()
        
        # Adjust for edge cases like "NC State" -> "North Carolina State", "UNC"
        clean_c_name = c_name.replace('university', '').replace('college', '').strip()
        
        if clean_school == clean_c_name or clean_school == s_name:
            return row['Nickname']
            
        if clean_school in c_name or clean_school in s_name or c_name in clean_school:
            return row['Nickname']
            
    # Hardcoded edge cases
    if "Miami (FL)" in school_name: return "Hurricanes"
    if "Miami (Ohio)" in school_name: return "RedHawks"
    if "NC State" in school_name: return "Wolfpack"
    if "Ole Miss" in school_name: return "Rebels"
    if "IU Indy" in school_name: return "Jaguars" 
    if "Purdue Fort Wayne" in school_name: return "Mastodons"
    if "UIC" in school_name: return "Flames"

    return "None"

print("Fetching Mascots from Wikipedia...")
url = "https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_institutions"
headers = {"User-Agent": "Mozilla/5.0"}
html = io.StringIO(requests.get(url, headers=headers).text)
tables = pd.read_html(html)

wiki_df = None
for t in tables:
    if len(t) > 100 and 'Nickname' in t.columns:
        wiki_df = t
        break

if wiki_df is not None:
    # Remove Wiki footnotes like [23] from Nicknames
    wiki_df['Nickname'] = wiki_df['Nickname'].apply(lambda x: re.sub(r'\[.*?\]', '', str(x)).strip())
    
    df = pd.read_csv("ncaa_d1_teams_initial.csv")
    
    df['Mascot'] = df['Mascot'].astype(str)
    
    found = 0
    missing = []
    
    for idx, row in df.iterrows():
        mascot = fuzzy_match(row['School'], wiki_df)
        df.loc[idx, 'Mascot'] = mascot
        
        if mascot != "None":
            found += 1
        else:
            missing.append(row['School'])
            
    df.to_csv("ncaa_d1_teams_initial.csv", index=False)
    print(f"Successfully matched {found} out of {len(df)} mascots!")
    if missing:
        print(f"Could not automatically match mascots for: {missing}")
else:
    print("Failed to load Wikipedia mascot table.")
