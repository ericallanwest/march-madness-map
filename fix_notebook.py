import json

def fix_notebook():
    file_path = 'ncaa_d1_google_sheets.ipynb'
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    for cell in nb.get('cells', []):
        if cell['cell_type'] == 'code':
            new_source = []
            for line in cell['source']:
                if "voronoi_diagram(team_points)" in line:
                    line = line.replace(
                        "voronoi_diagram(team_points)", 
                        "voronoi_diagram(team_points, envelope=us_boundary.unary_union.envelope)"
                    )
                new_source.append(line)
            cell['source'] = new_source
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f)
        
if __name__ == '__main__':
    fix_notebook()
