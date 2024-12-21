import pandas as pd

players_90_df = pd.read_csv("player_data_90d.csv")
player_data_all = pd.read_csv("player_data_all.csv")

players_90_df['tier_m'] = 0
players_90_df['region_m'] = 0

player_data_all['tier_m'] = 0
player_data_all['region_m'] = 0

player_data_all.to_csv("player_data_all.csv", index=False)
players_90_df.to_csv("player_data_90d.csv", index=False)