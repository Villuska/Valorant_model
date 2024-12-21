import pandas as pd
from file_helpers import *
import numpy as np
import ast

def team_strength_calculator(strength_90d, strength_all):
    # Read CSV files
    player_strength_90d = strength_90d
    player_strength_all = strength_all

    # Rename columns
    player_strength_90d = player_strength_90d.rename(columns={"Player_Strength": "Player_Strength_90d", "Total_Rounds_Played": "Total_Rounds_Played_90d"})
    player_strength_all = player_strength_all.rename(columns={"Player_Strength": "Player_Strength_All", "Total_Rounds_Played": "Total_Rounds_Played_All"})

    # Merge dataframes
    print(player_strength_90d.columns)
    print(player_strength_all.columns)
    player_strength = pd.merge(player_strength_90d, player_strength_all, on=["Player", "Team"])
    # Calculate Player_Strength
    player_strength['Player_Strength'] = player_strength.apply(
        lambda row: np.nan if row['Total_Rounds_Played_All'] <= 240 else
                    (0.35 * row['Player_Strength_90d'] + 0.65 * row['Player_Strength_All']) 
                    if row['Total_Rounds_Played_90d'] >= 120 else row['Player_Strength_All'],
        axis=1
    )

    player_strength = player_strength[['Player', 'Team', 'Player_Strength']]
    player_strength.to_csv("final_player_strength.csv", index=False)

    team_data = pd.read_csv("teams.csv")

    team_data['players'] = team_data['players'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Iterate over players to calculate strengths
    for i in range(1, 7):
        player_col = f"Player_{i}"
        strength_col = f"{player_col}_Strength"
        
        # Create a dictionary for fast lookup
        strength_dict = player_strength.set_index(['Team', 'Player'])['Player_Strength'].to_dict()
        
        # Extract the ith player from the players list (if it exists)
        team_data[player_col] = team_data['players'].apply(lambda players: players[i - 1] if len(players) >= i else None)
        
        # Debugging to ensure columns are correct
        print(team_data.columns)
        print(team_data.head())
        
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

    team_data.to_csv("Teams_with_Player_Strengths.csv", index=False)

    # Calculate Team_Strength
    team_data['Team_Strength'] = team_data[[col for col in team_data.columns if col.endswith('_Strength')]].mean(axis=1, skipna=True)
    team_data = team_data[['team', 'Team_Strength']]

    # Rename specific teams
    team_data['team'] = team_data['team'].replace({"KR?o Esports": "KRU Esports", "Leviatán": "Leviatan"})



    # Save final team strengths
    team_data = team_data.sort_values(by='Team_Strength', ascending=False)
    team_data.to_csv("initial_strengths.csv", index=False)
    save_df_as_csv(team_data, 'firepowers', 'firepower_history')

def main():
    df_90d = pd.read_csv("player_strengths_90d.csv")
    df_all = pd.read_csv("player_strengths_all.csv")
    team_strength_calculator(df_90d, df_all)

if __name__ == "__main__":
    main()