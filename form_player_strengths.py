import pandas as pd
from file_helpers import *

def player_strength_calculator(file, save_file_name):
    # Read the player stats file
    player_stats = pd.read_csv(file)

    # Ensure calculations only happen for players who have played at least one round
    player_stats_filtered = player_stats[player_stats['Total_Rounds_Played'] != 0].copy()

    player_stats_filtered['Rating'] = player_stats_filtered['Rating'] * 90
    player_stats_filtered['ACS'] = player_stats_filtered['ACS'] * 0.5
    player_stats_filtered['FKPR'] = player_stats_filtered['FKPR'] * 100
    player_stats_filtered['FDPR'] = player_stats_filtered['FDPR'] * -100

    # Calculate Player Strength directly using raw stats and given weight multipliers
    player_strength = pd.DataFrame({
        'Player': player_stats_filtered['Player'],
        'Team': player_stats_filtered['Team'],
        'Player_Strength': ((player_stats_filtered['Rating'] * 0.5 +
                             player_stats_filtered['ACS'] * 0.4 +
                             player_stats_filtered['FKPR'] * 0.1 +
                             player_stats_filtered['FDPR'] * -0.05) *  # FDPR has negative weight
                            player_stats_filtered['tier_m'] *
                            player_stats_filtered['region_m']).round(2),
        'Total_Rounds_Played': player_stats_filtered['Total_Rounds_Played']
    })
    
    # Sort player strength in descending order
    player_strength = player_strength.sort_values(by='Player_Strength', ascending=False)
    player_strength = player_strength.drop_duplicates(subset=['Player', 'Team'], keep='last')
    # Save to file
    player_strength = player_strength.round(2)
    player_strength.to_csv(save_file_name, index=False)
    return player_strength

def form_player_strengths():
    player_strengths_all = player_strength_calculator("player_data_all.csv", "player_strengths_all.csv")
    player_strengths_90_d = player_strength_calculator("player_data_90d.csv", "player_strengths_90d.csv")
