import pandas as pd
import numpy as np
from scipy.spatial import Voronoi
import networkx as nx

def resolve_voronoi_color_overlaps():
    print("Loading team coordinates...")
    target_file = 'ncaa_d1_teams_initial.csv'
    df = pd.read_csv(target_file)
    
    # Extract the Lat/Lon coordinates into a numpy array
    points = df[['Lon', 'Lat']].values

    # Add dummy bounding points to contain the infinite Voronoi regions
    large_val = 1000
    dummy_points = np.array([
        [-large_val, -large_val],
        [-large_val, large_val],
        [large_val, -large_val],
        [large_val, large_val]
    ])
    all_points = np.vstack([points, dummy_points])

    # Generate the Voronoi mesh
    print("Building spatial Voronoi mesh to detect geographical neighbors...")
    vor = Voronoi(all_points)

    # Initialize a NetworkX graph to represent territorial borders
    G = nx.Graph()
    for i in range(len(points)):
        G.add_node(i)

    # Map every single adjacent border sharing property
    for ridge_points in vor.ridge_points:
        p1, p2 = ridge_points
        # Ignore bounds
        if p1 < len(points) and p2 < len(points):
            G.add_edge(p1, p2)

    print("Running greedy graph coloring algorithm to guarantee distinct borders...")
    # Apply standard greedy coloring. This typically only requires 4-5 indices
    color_map = nx.greedy_color(G, strategy='largest_first')

    # The 12 original vibrant palette choices
    color_pairs = [
        ("#CC0000", "#000000"), ("#0033A0", "#FFFFFF"), ("#00274C", "#FFCB05"),
        ("#C8102E", "#F1BE48"), ("#E84A27", "#13294B"), ("#C5050C", "#FFFFFF"),
        ("#FF8200", "#FFFFFF"), ("#003087", "#FFFFFF"), ("#18453B", "#FFFFFF"),
        ("#4D1979", "#FFFFFF"), ("#FFCD00", "#000000"), ("#000000", "#BA9B37")
    ]

    # Assign guaranteed non-overlapping palette choices back to the dataframe
    for idx in range(len(points)):
        graph_assigned_color_index = color_map[idx]
        
        # We index safely into our palette
        c1, c2 = color_pairs[graph_assigned_color_index % len(color_pairs)]
        df.loc[idx, 'Hex'] = c1
        df.loc[idx, 'Hex2'] = c2

    # Save to CSV
    df.to_csv(target_file, index=False)
    print("Success! No two touching territories in the USA will ever share the exact same color again.")

if __name__ == "__main__":
    resolve_voronoi_color_overlaps()
