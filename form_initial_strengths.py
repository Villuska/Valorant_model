import pandas as pd
from file_helpers import *
import numpy as np
import ast

def scale_value(x, in_min=100, in_max=300, out_min=0.01, out_max=0.35):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min


def all_recent_scaler(row):
    recent_rounds = row['Total_Rounds_Played_90d']
    all_rounds = row['Total_Rounds_Played_All']
    strength_all = row['Player_Strength_All']
    strength_recent = row['Player_Strength_90d']
    if all_rounds <= 300:
        strength = np.nan
    elif recent_rounds < 100:
        strength = strength_all
    else:
        recent_m = scale_value(row['Total_Rounds_Played_90d'])
        strength = recent_m * strength_recent + (1-recent_m) * strength_all
    return strength

def team_strength_calculator(strength_90d, strength_all):
    # Read CSV files
    player_strength_90d = strength_90d
    player_strength_all = strength_all

    # Rename columns
    player_strength_90d = player_strength_90d.rename(columns={"Player_Strength": "Player_Strength_90d", "Total_Rounds_Played": "Total_Rounds_Played_90d"})
    player_strength_all = player_strength_all.rename(columns={"Player_Strength": "Player_Strength_All", "Total_Rounds_Played": "Total_Rounds_Played_All"})

    # Merge dataframes
    player_strength = pd.merge(player_strength_90d, player_strength_all, on=["Player", "Team"])
    # Calculate Player_Strength
    player_strength['Player_Strength'] = player_strength.apply(all_recent_scaler, axis=1)

    player_strength = player_strength[['Player', 'Team', 'Player_Strength']]
    player_strength = player_strength.sort_values(by='Player_Strength', ascending=False, inplace=False).round(2)
    player_strength.to_csv("final_player_strength.csv", index=False)

    team_data = pd.read_csv("teams.csv")

    team_data['players'] = team_data['players'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Iterate over players to calculate strengths
    team_data['player_count'] = team_data['players'].apply(len)

    for i in range(1, 7):
        player_col = f"Player_{i}"
        strength_col = f"{player_col}_Strength"
        
        # Create a dictionary for fast lookup
        strength_dict = player_strength.set_index(['Team', 'Player'])['Player_Strength'].to_dict()
        
        # Extract the ith player from the players list (if it exists)
        team_data[player_col] = team_data['players'].apply(lambda players: players[i - 1] if len(players) >= i else None)
        
        # Apply strength calculation
        team_data[strength_col] = team_data.apply(
            lambda row: strength_dict.get((row['team'], row[player_col]), None), axis=1
        )

    # Apply conditions to specific player strengths
    team_data['Player_4_Strength'] = team_data['Player_4_Strength'].where(team_data['Player_4_Strength'] >= 0, None)
    team_data['Player_5_Strength'] = team_data['Player_5_Strength'].where(team_data['Player_5_Strength'] >= 0, None)
    team_data['Player_6_Strength'] = team_data['Player_6_Strength'].where(
        (team_data['Player_6_Strength'] >= 0) & (team_data['Player_6'] != "Lara"), None
    )
    team_data = team_data[team_data['player_count'] >= 5]
    team_data.to_csv("teams_with_Player_Strengths.csv", index=False)

    # Calculate Team_Strength
    team_data['Team_Strength'] = team_data[[col for col in team_data.columns if col.endswith('_Strength')]].mean(axis=1, skipna=True)

    team_data = team_data[['team', 'Team_Strength', 'tier', 'region', 'player_count']]
    team_data = team_data.rename(columns={'Team_Strength': 'team_strength'})

    # Rename specific teams
    team_data['team'] = team_data['team'].replace({"KR?o Esports": "KRU Esports", "Leviatán": "Leviatan"})



    # Save final team strengths
    team_data = team_data.sort_values(by='team_strength', ascending=False)
    team_data = team_data.drop_duplicates(subset=['team'], keep='last')
    team_data = team_data.round(2)
    team_data.to_csv("initial_strengths.csv", index=False)
    save_df_as_csv(team_data, 'firepowers', 'firepower_history')

def form_initial_strengths():
    df_90d = pd.read_csv("player_strengths_90d.csv")
    df_all = pd.read_csv("player_strengths_all.csv")
    team_strength_calculator(df_90d, df_all)

form_initial_strengths()