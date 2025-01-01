import pandas as pd
import math
from match_helpers import *


teams_and_elos = pd.read_csv("initial_strengths.csv")

def start(team1, team2, map_count):
    
    team1_s = teams_and_elos[teams_and_elos['team'] == team1]
    team2_s = teams_and_elos[teams_and_elos['team'] == team2]
    team1_str = team1_s['team_strength'].values[0]
    team2_str = team2_s['team_strength'].values[0]
    """
    if subs_t1 != "":
        team1_str = get_strength_with_sub(team1, team1_s['Region'].values[0])
    else:
        team1_str = team1_s['strength'].values[0]
    if subs_t2 != "":
        team2_str = get_strength_with_sub(team2, team2_s['Region'].values[0])
    else:
        team2_str = team2_s['strength'].values[0]
    """

    print("")
    print(team1, team2)
    print(team1_str, team2_str, round(team1_str-team2_str,2))

    #team1 = input("Enter team1: ").lower() 
    #team2 = input("Enter team2: ").lower()
    #maps_count = input("Enter bo(x): ")
    if map_count == "":
        map_count = 3
        
    if map_count == 1:
        winrate_func_bo1(team1, team2, team1_str, team2_str)
    elif map_count == 3:
        winrate_func_bo3(team1, team2, team1_str, team2_str)
    elif map_count == 5:
        winrate_func_bo5(team1, team2, team1_str, team2_str)
    else:
        winrate_func_bo3(team1, team2, team1_str, team2_str)


team1 = input("Fav team: ")
#subs_t1 = input("Are there any subs? ") 
team2 = input("Dog team: ")
#subs_t2 = input("Are there any subs? ") 
map_count = int(input("How many maps? "))
start(team1, team2, map_count)

