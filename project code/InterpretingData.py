import pandas as pd
import re

# Load data
df = pd.read_csv('./charting-m-points-2020s.csv')

def get_valid_serve_code(row):
    first = row['1st']
    second = row['2nd']

    # Reject fault codes for first serve
    if first and not str(first).startswith(('n', 'w', 'd', 'x', 'g', 'e', '!')):
        if re.match(r'[456]', str(first)):  # direction exists
            return first

    # Otherwise try second serve
    if second and not str(second).startswith(('n', 'w', 'd', 'x', 'g', 'e', '!')):
        if re.match(r'[456]', str(second)):
            return second

    return None

def extract_serve_direction(serve_code):
    if pd.isna(serve_code):
        return None
    # Exclude serves that start with a known fault indicator
    if serve_code[0] in ['n', 'w', 'd', 'x', 'g', 'e', '!']:
        return None
    # Parse the first digit for direction
    match = re.match(r'(\d)', serve_code)
    if match:
        direction = match.group(1)
        if direction == '4':
            return 'Wide'
        elif direction == '5':
            return 'Body'
        elif direction == '6':
            return 'T'
    return None

def extract_return_direction(rally_code):
    if pd.isna(rally_code):
        return None

    # Remove the serve code (which comes first) to isolate the rally
    serve_pattern = re.match(r'^[456]', rally_code)
    if serve_pattern:
        rally_code = rally_code[1:]  # Remove 1 char serve direction

    # Search for the first valid return shot followed by a digit
    match = re.search(r'[fbrsvzhijklm][123]', rally_code)
    if match:
        direction = match.group()[-1]
        if direction == '1':
            return 'Line'
        elif direction == '2':
            return 'Middle'
        elif direction == '3':
            return 'Cross'
    return None

def get_point_outcome(svr, pt_winner):
    if pd.isna(svr) or pd.isna(pt_winner): return None
    return 'Server' if int(svr) == int(pt_winner) else 'Returner'

def extract_players(match_id):
    try:
        # Get the last two hyphen-separated segments
        parts = match_id.split('-')
        player_str = '-'.join(parts[-2:])
        player1, player2 = player_str.split('-')

        # Extract only last names (after the last underscore)
        last1 = player1.split('_')[-1].lower()
        last2 = player2.split('_')[-1].lower()
        return last1, last2
    except:
        return None, None


# Extract player names
df['Player1'], df['Player2'] = zip(*df['match_id'].apply(extract_players))

# Build processed dataset
processed_rows = []
for _, row in df.iterrows():
    # serve_code = row['1st'] if not pd.isna(row['1st']) and any(c in row['1st'] for c in ['w', 't', 'b']) else row['2nd']
    serve_code = get_valid_serve_code(row)
    rally_code = row['1st'] if 'r' in str(row['1st']) else row['2nd']

    serve_dir = extract_serve_direction(serve_code)
    return_dir = extract_return_direction(rally_code)
    outcome = get_point_outcome(row['Svr'], row['PtWinner'])

    if serve_dir and return_dir and outcome:
      winner = row['Player1'] if int(row['PtWinner']) == 1 else row['Player2']
      processed_rows.append({
          'MatchID': row['match_id'],
          'Pt': row['Pt'],
          'Pts': row['Pts'],
          'Svr': row['Svr'],
          'Player1': row['Player1'],
          'Player2': row['Player2'],
          'ServeDirection': serve_dir,
          'ReturnDirection': return_dir,
          'PointOutcome': outcome,
          'WinnerName': winner
      })

# Convert to DataFrame
points_df = pd.DataFrame(processed_rows)
points_df.head()
