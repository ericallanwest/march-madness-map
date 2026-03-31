$notebookPath = "c:\Users\Eric\Desktop\Ideas\March_Madness\march-madness-map\ncaa_20260318.ipynb"
$json = Get-Content -Raw $notebookPath | ConvertFrom-Json -Depth 10

# Find the cell that defines csv_data
foreach ($cell in $json.cells) {
    if ($cell.cell_type -eq "code" -and $cell.source -match "csv_data = ") {
        # Update the source code array
        $newSource = @(
            "sheet_url = `'https://docs.google.com/spreadsheets/d/<YOUR_SHEET_ID>/export?format=csv`'`n",
            "print(`f`"Downloading from Google Sheet...`")`n",
            "all_teams_df = pd.read_csv(sheet_url)`n",
            "`n",
            "print(`f`"Loaded {len(all_teams_df)} teams from Google Sheets!`")"
        )
        $cell.source = $newSource
        
        # We also need to clear outputs as they represent old state
        $cell.outputs = @()
        break
    }
}

# Find the cell that calls export_round_geojson(32) and update comments
foreach ($cell in $json.cells) {
    if ($cell.cell_type -eq "code") {
        for ($i=0; $i -lt $cell.source.Count; $i++) {
            if ($cell.source[$i] -match "rounds =.*\[68, 64, 32, 16\]") {
                 $cell.source[$i] = "rounds = [362, 68, 64, 32, 16]`n"
            }
        }
    }
}

# The ConvertTo-Json in PS has some escaping quirks for < and >, but Jupyter mostly ignores them.
$json | ConvertTo-Json -Depth 10 -Compress | Set-Content -Path $notebookPath -Encoding UTF8
Write-Output "Successfully updated the notebook!"
