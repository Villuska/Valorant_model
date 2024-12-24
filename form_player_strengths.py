import pandas as pd
from file_helpers import *

def player_strength_calculator(file, save_file_name):
    # Read the player stats files
    player_stats = pd.read_csv(file)

    
    # Calculate summary statistics for the data
    stats_to_summarize = ['Rating', 'ACS', 'KD', 'ADR', 'KAST', 'KPR', 'APR', 'FKPR', 'FDPR']
    player_stats_sum = player_stats[player_stats['Total_Rounds_Played'] != 0].agg(
        {stat: ['mean', 'std'] for stat in stats_to_summarize}
    )
    
    # Create a flattened dictionary of summary statistics
    player_stats_sum_flat = {f"{stat}_{func}": player_stats_sum[stat][func] for stat in stats_to_summarize for func in ['mean', 'std']}
    
    # Calculate z-scores for player stats
    player_stats_zscores = player_stats.copy()
    for stat in stats_to_summarize:
        player_stats_zscores[stat] = (player_stats[stat] - player_stats_sum_flat[f"{stat}_mean"]) / player_stats_sum_flat[f"{stat}_std"] * 25 + 100
    player_stats_zscores['FDPR'] = (player_stats['FDPR'] - player_stats_sum_flat['FDPR_mean']) / player_stats_sum_flat['FDPR_std'] * -25 + 100

    # Calculate Player Strength with multipliers and rounding
    player_strength = pd.DataFrame({
        'Player': player_stats_zscores['Player'],
        'Team': player_stats_zscores['Team'],
        'Player_Strength': ((player_stats_zscores['Rating'] * 0.5 +
                             player_stats_zscores['ACS'] * 0.2 +
                             player_stats_zscores['ADR'] * 0.075 +
                             player_stats_zscores['APR'] * 0.075 +
                             player_stats_zscores['FKPR'] * 0.1 +
                             player_stats_zscores['FDPR'] * 0.05) *
                            player_stats_zscores['tier_m'] *
                            player_stats_zscores['region_m']).round(2),
        'Total_Rounds_Played': player_stats_zscores['Total_Rounds_Played']
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

form_player_strengths()