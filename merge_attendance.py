import pandas as pd
import os

def merge_attendance():
    ncaa_file = 'attendance.csv'
    target_file = 'ncaa_d1_teams_initial.csv'
    
    if not os.path.exists(ncaa_file):
        print(f"File '{ncaa_file}' not found! Please download the official CSV from stats.ncaa.org and save it as '{ncaa_file}'")
        return

    # Load both CSVs
    try:
        att_df = pd.read_csv(ncaa_file)
        df = pd.read_csv(target_file)
    except Exception as e:
        print(f"Error reading CSVs: {e}")
        return

    # The NCAA stats usually have columns 'Team' and 'Avg' or 'Avg.'
    # We need to find the right column names in the official export
    team_col_cands = [c for c in att_df.columns if 'team' in str(c).lower() or 'institution' in str(c).lower()]
    team_col = team_col_cands[0] if team_col_cands else att_df.columns[1]
    avg_col = [c for c in att_df.columns if 'avg' in str(c).lower()][0]

    import difflib
    missing = []
    found = 0

    ncaa_teams = att_df[team_col].astype(str).tolist()
    
    for idx, row in df.iterrows():
        school = str(row['School']).strip()
        best_match = None
        
        # 1. Exact or Substring
        for nt in ncaa_teams:
            if nt.lower() == school.lower() or nt.lower() in school.lower() or school.lower() in nt.lower():
                best_match = nt
                break
                
        # 2. Fuzzy Match
        if not best_match:
            matches = difflib.get_close_matches(school, ncaa_teams, n=1, cutoff=0.7)
            if matches:
                best_match = matches[0]

        if best_match:
            match_row = att_df[att_df[team_col] == best_match]
            val_str = str(match_row.iloc[0][avg_col]).replace(',', '')
            try:
                avg_att = int(float(val_str))
                df.loc[idx, 'Avg_Attendance'] = avg_att
                found += 1
            except ValueError:
                pass
        else:
            missing.append(school)

    # Save results
    df.to_csv(target_file, index=False)
    print(f"Successfully updated Avg_Attendance for {found} teams out of {len(df)}!")
    if missing:
        print(f"Could not automatically match attendance for: {missing}")

if __name__ == "__main__":
    print("Attempting to merge official NCAA attendance data...")
    merge_attendance()
