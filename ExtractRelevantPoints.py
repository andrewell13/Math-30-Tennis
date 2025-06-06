# Define last names of interest
target_players = {'sinner', 'griekspoor'}

# Filter to only include matches between those two players
filtered_df = points_df[
    (points_df['Player1'].isin(target_players)) &
    (points_df['Player2'].isin(target_players))
]

# Determine if point was on even (deuce) or odd (ad) side
def is_even_point(score_str):
    score_map = {'0': 0, '15': 1, '30': 2, '40': 3, 'A': 4}
    try:
        server_pts, returner_pts = score_str.split('-')
        s = score_map.get(server_pts.strip(), 0)
        r = score_map.get(returner_pts.strip(), 0)
        return (s + r) % 2 == 0
    except:
        return True

# Define what counts as serving/returning to the right
def served_to_right(serve_dir, is_even):
    return (is_even and serve_dir == 'T') or (not is_even and serve_dir == 'Wide')

def returned_to_right(return_dir, is_even):
    return (is_even and return_dir == 'Line') or (not is_even and return_dir == 'Cross')

filtered_df['IsEven'] = filtered_df['Pts'].apply(is_even_point)
filtered_df['ServeRight'] = filtered_df.apply(lambda row: served_to_right(row['ServeDirection'], row['IsEven']), axis=1)
filtered_df['ReturnRight'] = filtered_df.apply(lambda row: returned_to_right(row['ReturnDirection'], row['IsEven']), axis=1)

# Build match_points array
match_points = []

for _, row in filtered_df.iterrows():
    if pd.notna(row['ServeRight']) and pd.notna(row['ReturnRight']) and pd.notna(row['PointOutcome']):
        match_points.append({
            'pt': row['Pt'],  # Add point number
            'serve_direction': 'R' if row['ServeRight'] else 'L',
            'return_direction': 'R' if row['ReturnRight'] else 'L',
            'winner': row['PointOutcome']  # 'Server' or 'Returner'
        })

from pprint import pprint
pprint(match_points[:5])
