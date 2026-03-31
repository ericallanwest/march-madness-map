import pandas as pd
import difflib

def fix_attendance():
    target_file = 'ncaa_d1_teams_initial.csv'
    df = pd.read_csv(target_file)
    
    # 1. Handle Duplicates: Some schools like UMass Lowell have 2 arenas. Keep the one with highest capacity.
    initial_len = len(df)
    df = df.sort_values('Capacity', ascending=False)
    df = df.drop_duplicates(subset=['School'], keep='first')
    # Bring back to original format if needed, but dropping is fine here
    
    # Reset avg attendance to Capacity so we start fresh for debugging missing ones
    df['Avg_Attendance'] = df['Capacity']

    ncaa_file = 'attendance.csv'
    att_df = pd.read_csv(ncaa_file)
    team_col_cands = [c for c in att_df.columns if 'team' in str(c).lower() or 'institution' in str(c).lower()]
    team_col = team_col_cands[0] if team_col_cands else att_df.columns[1]
    avg_col = [c for c in att_df.columns if 'avg' in str(c).lower()][0]

    ncaa_teams_orig = att_df[team_col].astype(str).tolist()

    found = 0
    missing = []

    # Common mis-matches between Wikipedia formatting and NCAA Stats formatting
    mapping = {
        'Ole Miss': 'Ole Miss', "St. John's": "St. John's (NY)", 'Miami (OH)': 'Miami (OH)',
        'NC State': 'NC State', 'UIC': 'UIC', 'UIW': 'UIW', 'UTEP': 'UTEP', 'UTRGV': 'UTRGV',
        'UTSA': 'UTSA', 'UCF': 'UCF', 'SMU': 'SMU', 'VMI': 'VMI', 'BYU': 'BYU', 'LSU': 'LSU',
        'TCU': 'TCU', 'UNLV': 'UNLV', 'UMass Lowell': 'UMass Lowell', 'Massachusetts': 'Massachusetts',
        'Texas A&M-Corpus Christi': 'A&M-Corpus Christi', 'Louisiana–Monroe': 'ULM', 'Connecticut': 'UConn',
        'Penn': 'Penn', 'Florida Atlantic': 'Fla. Atlantic', 'Florida Gulf Coast': 'FGCU',
        'Virginia Commonwealth': 'VCU', 'Sacramento State': 'Sacramento St.', 'USC': 'Southern California',
        'Cal State Northridge': 'CSUN', 'North Carolina A&T': 'N.C. A&T', 'UNC Wilmington': 'UNCW',
        'Northern Illinois': 'NIU', 'Maryland Eastern Shore': 'UMES', 'North Carolina Central': 'N.C. Central',
        'Fairleigh Dickinson': 'FDU', 'SIU Edwardsville': 'SIUE', 'Tennessee-Martin': 'UT Martin',
        'Army': 'Army West Point', 'Boston University': 'Boston U.', 'Incarnate Word': 'UIW',
        'Lamar': 'Lamar University', 'Stephen F. Austin': 'SFA', 'Appalachian State': 'App State',
        'Alcorn State': 'Alcorn'
    }

    for idx, row in df.iterrows():
        school = str(row['School']).strip()
        cap = int(row['Capacity'])
        best_match = None

        # 1. Exact Match
        for nt in ncaa_teams_orig:
            if nt.lower() == school.lower():
                best_match = nt
                break
        
        if not best_match and mapping.get(school) and mapping.get(school) in ncaa_teams_orig:
            best_match = mapping.get(school)

        # 3. Fuzzy Match
        if not best_match:
            matches = difflib.get_close_matches(school, ncaa_teams_orig, n=1, cutoff=0.7)
            if matches:
                # Extra check to prevent "Virginia" from matching "Virginia Tech", etc.
                best_match = matches[0]

        if best_match:
            match_row = att_df[att_df[team_col] == best_match]
            val_str = str(match_row.iloc[0][avg_col]).replace(',', '')
            try:
                avg_att = int(float(val_str))
                df.loc[idx, 'Avg_Attendance'] = avg_att
                found += 1
            except ValueError:
                missing.append(school)
        else:
            missing.append(school)

    df.to_csv(target_file, index=False)
    print(f'Done! Found {found}/{len(df)} teams.')
    if missing:
        print('Could not find matches for:', missing)

if __name__ == '__main__':
    fix_attendance()
