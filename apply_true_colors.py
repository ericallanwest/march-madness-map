import requests
import pandas as pd
import difflib

def fetch_and_apply_colors():
    print("Fetching true NCAA Men's Basketball Hex Colors from ESPN API...")
    url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams?limit=400"
    try:
        data = requests.get(url).json()
    except Exception as e:
        print("Failed to contact ESPN API:", e)
        return

    # Extract all D1 teams into a fast lookup list
    espn_teams = data.get('sports', [])[0].get('leagues', [])[0].get('teams', [])
    
    # We want to match efficiently. ESPN provides name (e.g. 'Tar Heel'), shortDisplayName ('N Carolina'), displayName ('North Carolina')
    # We will build a prioritized matching system.
    team_dict = {}
    espn_names = []
    
    for t in espn_teams:
        team_data = t.get('team', {})
        short_name = team_data.get('shortDisplayName')
        display_name = team_data.get('displayName')
        location = team_data.get('location')
        
        color1 = "#" + team_data.get('color', '000000')
        color2 = "#" + team_data.get('alternateColor', str(color1)) # duplicate if no alt
        
        # Save to lookup
        if display_name:
            team_dict[display_name] = (color1, color2)
            espn_names.append(display_name)
        if location:
            team_dict[location] = (color1, color2)
            espn_names.append(location)
        if short_name:
            team_dict[short_name] = (color1, color2)
            espn_names.append(short_name)

    # Clean duplicates
    espn_names = list(set(espn_names))

    print(f"Built ESPN dictionary with {len(espn_names)} unique search terms.")

    target_file = 'ncaa_d1_teams_initial.csv'
    df = pd.read_csv(target_file)
    initial_found = 0
    missing = []

    # Some difficult cases that fuzzy matching struggles with
    mapping = {
        'Ole Miss': 'Ole Miss', "St. John's": "St. John's", 'Miami (OH)': 'Miami (OH)',
        'NC State': 'NC State', 'UIC': 'UIC Flames', 'UIW': 'Incarnate Word', 'UTEP': 'UTEP', 'UTRGV': 'UT Rio Grande Valley',
        'UTSA': 'UTSA', 'UCF': 'UCF', 'SMU': 'SMU', 'VMI': 'VMI', 'BYU': 'BYU', 'LSU': 'LSU',
        'TCU': 'TCU', 'UNLV': 'UNLV', 'UMass Lowell': 'UMass Lowell', 'Massachusetts': 'Massachusetts',
        'A&M-Corpus Christi': 'Tex A&M-CC', 'Louisiana–Monroe': 'UL Monroe', 'UConn': 'UConn',
        'Penn': 'Penn', 'Florida Atlantic': 'Florida Atlantic', 'Florida Gulf Coast': 'FGCU',
        'Virginia Commonwealth': 'VCU', 'Sacramento State': 'Sacramento State', 'USC': 'USC',
        'Cal State Northridge': 'CSU Northridge', 'North Carolina A&T': 'NC A&T', 'UNC Wilmington': 'UNC Wilmington',
        'Northern Illinois': 'Northern Illinois', 'Maryland Eastern Shore': 'UMES', 'North Carolina Central': 'NC Central',
        'Fairleigh Dickinson': 'FDU', 'SIU Edwardsville': 'SIU Edwardsville', 'Tennessee-Martin': 'UT Martin',
        'Army West Point': 'Army', 'Boston University': 'Boston U', 'Incarnate Word': 'Incarnate Word',
        'Lamar University': 'Lamar', 'SFA': 'Stephen F. Austin', 'App State': 'Appalachian State',
        'Alcorn State': 'Alcorn', 'Southern Miss': 'Southern Miss', 'UAB': 'UAB', 'UT Arlington': 'UT Arlington',
        'Vanderbilt': 'Vanderbilt'
    }

    for idx, row in df.iterrows():
        school = str(row['School']).strip()
        best_match = None
        
        # 0. Check strict hardcoded maps which override fuzzy assumptions
        if mapping.get(school):
            mapped_val = mapping[school]
            if mapped_val in team_dict:
                best_match = mapped_val
                
        # 1. Exact Name / Location Match in ESPN dictionary
        if not best_match and school in team_dict:
            best_match = school
            
        # 2. Contains match
        if not best_match:
            for en in espn_names:
                if en.lower() == school.lower():
                    best_match = en
                    break
                    
        # 3. Target Fuzzy match
        if not best_match:
            matches = difflib.get_close_matches(school, espn_names, n=1, cutoff=0.7)
            if matches:
                 best_match = matches[0]

        if best_match and best_match in team_dict:
            c1, c2 = team_dict[best_match]
            df.loc[idx, 'Hex'] = c1
            df.loc[idx, 'Hex2'] = c2
            initial_found += 1
        else:
            missing.append(school)

    # Final cleanup logic for any truly missing teams from ESPN
    manual_colors = {
        'Southeastern Louisiana': ('#00654c', '#eeb111'),
        'Lindenwood': ('#b5a36a', '#000000'),
        'LIU': ('#69b3e7', '#f2c75c'),
        'Queens': ('#00205b', '#c4b581')
    }

    for m in missing:
        idx = df[df['School'] == m].index[0]
        if m in manual_colors:
            c1, c2 = manual_colors[m]
        else:
            c1, c2 = ("#444444", "#ffffff")
        df.loc[idx, 'Hex'] = c1
        df.loc[idx, 'Hex2'] = c2

    df.to_csv(target_file, index=False)
    print(f"Applied true Hex colors for {initial_found}/{len(df)} schools!")
    if missing:
        print("Missing (Assigned defaulting colors to avoid errors):", missing)

if __name__ == '__main__':
    fetch_and_apply_colors()
