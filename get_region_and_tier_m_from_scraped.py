import pandas as pd
from constants import *
import ast




def get_opponents_tier_and_region(row, teams_df):
    
    if pd.notna(row['opponents']):
        name = row['Player']
        opponents = ast.literal_eval(row['opponents'])
        team_names = list(teams_df['team'])
        tiers = []
        regions = []
        if type(opponents) == list:
            for opp in opponents:
                if opp in team_names:
                    opp_row = teams_df[teams_df["team"] == opp]
                    if not opp_row.empty:
                        opp_region = opp_row['region'].values[0]
                        opp_tier = opp_row['tier'].values[0]
                        if opp_region and pd.notna(opp_region):
                            regions.append(opp_region)
                        else:
                            teams_df = teams_df.apply(eval)
                            def find_player_row(player_name):
                                return teams_df[teams_df["players"].apply(lambda x: player_name in x)]
                            try:
                                team_row = find_player_row(row['Player'])
                                region = team_row['Region']
                            except Exception as e:
                                region = "Indonesia"
                            regions.append(region)

                        if opp_tier and pd.notna(opp_tier):
                            tiers.append(opp_tier)
                        else:
                            tiers.append("Tier 3")
                    else:
                        tiers.append("Tier 3")
                        regions.append("North America")
                else:
                    tiers.append("Tier 3")
                    regions.append("North America")

            tier_m, region_m = get_tier_region_multi(tiers, regions)
            """
            if name == "RedKoh":
                print(opponents)
                print(tier_m, region_m)
                print(tiers)
                print(regions)
                print(len(opponents))
                print(len(tiers))
                print(len(regions))
            """
            return tier_m, region_m
    return 0.65, 0.65

    

def get_tier_region_multi(tiers, regions):
    """
    Input: list of tiers and regions
    Output: Average of multipliers
    _ADJUSTMENTS: dictionary of tier and region adjustments (multipliers)
    """
    tier_ms = [TIER_ADJUSTMENTS[tier] for tier in tiers if tier in TIER_ADJUSTMENTS]
    region_ms = [REGION_ADJUSTMENTS[reg] for reg in regions if reg in REGION_ADJUSTMENTS]
    
    effective_tier_m = sum(tier_ms) / len(tier_ms) if tier_ms else 0.65
    effective_reg_m = sum(region_ms) / len(region_ms) if region_ms else 0.65
    
    return round(effective_tier_m, 3), round(effective_reg_m, 3)


def apply_region_and_tier_m():
    teams_df = pd.read_csv("teams.csv")
    players_90_df = pd.read_csv("player_data_90d.csv").drop(columns=["Unnamed: 0"], errors="ignore")
    players_all_df = pd.read_csv("player_data_all.csv").drop(columns=["Unnamed: 0"], errors="ignore")
    for index, row in players_all_df.iterrows():
        name = row['Player']
        team = row['Team']
        
        # Get updated tier and region values
        tier_m, region_m = get_opponents_tier_and_region(row, teams_df)
        
        # Update players_all_df using index
        players_all_df.loc[index, "region_m"] = region_m 
        players_all_df.loc[index, "tier_m"] = tier_m
        if name == "RedKoh":
            print(tier_m, region_m)
        # Update players_90_df using name and team match
        players_90_df.loc[
            (players_90_df["Player"] == name) & (players_90_df["Team"] == team), 
            ["region_m", "tier_m"]
        ] = [region_m, tier_m]
    
    return players_all_df, players_90_df

