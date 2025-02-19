import pandas as pd
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import datetime
from constants import *
import math

teams_df = pd.read_csv("teams.csv")
players_df = pd.read_csv("players.csv")


def get_match_opponent(div):
    """ Input: div element from soup
        Output: opponents name in div element
    """
    lista = div.text.strip().replace("\t", "").split("\n")
    lista2 = []
    for item in lista:
        if item != "":
            lista2.append(item)
    opponent_name = lista2[8]
    opponent_name2 = lista2[9]
    if opponent_name == "0" or opponent_name == "1" or opponent_name == "2" or opponent_name == "3":
        opponent_name = opponent_name2


    return opponent_name

def get_opponents(url, row = None):
    """ Input: player url in timespan=all mode
        Output: List of opponents in a players match history
    """
    #url = row['url']
    if not type(url) == float:
        url = url.replace("?timespan=all", "").replace("/player", "/player/matches")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        try:    
            divs = soup.find_all('div', class_="mod-dark")

            if not divs:
                print("No elements with class 'mod-dark' found.")
                return []

            # Proceed with the first div
            parent_div = divs[0]
            inner_divs = parent_div.find_all('div', recursive=False)
            opponents = []
            for div in inner_divs:
                opponents.append(get_match_opponent(div))

            return opponents
        except TypeError:
            return []
    else:
        return []
    

def get_opponents_tier_and_region(url):
    """
    Input: Player url in timespan=all format
    Output: list of tiers and regions of players opponents in match history
    """
    print(url)
    opponents = get_opponents(url)
    team_names = list(teams_df['team'])
    tiers = []
    regions = []
    if opponents:
        for opp in opponents:
            if opp in team_names:
                opp_row = teams_df[teams_df["team"] == opp]
                opp_region = opp_row['region'].values[0]
                opp_tier = opp_row['tier'].values[0]
                if opp_region and pd.notna(opp_region):
                    regions.append(opp_region)
                if opp_tier and pd.notna(opp_tier):
                    tiers.append(opp_tier)
        return tiers, regions, opponents
    else:
        return [], [], opponents

def get_tier_region_multi(tiers, regions):
    """
    Input: list of tiers and regions
    Output: Average of multipliers
    _ADJUSTMENTS: dictionary of tier and region adjusments(multipliers)
    """
    tier_ms = []
    region_ms = []
    for tier in tiers:
        tier_m = TIER_ADJUSTMENTS.get(tier, 0.7)  # Default to 0.7 if tier not found
        tier_ms.append(tier_m)

    for reg in regions:
        reg_m = REGION_ADJUSTMENTS.get(reg, 0.7)  # Default to 0.7 if region not found
        region_ms.append(reg_m)

    if not len(tier_ms) == 0:
        effective_tier_m = sum(tier_ms) / len(tier_ms)
    else:
        effective_tier_m = 0.82

    if not len(region_ms) == 0:
        effective_reg_m = sum(region_ms) / len(region_ms)
    else:
        effective_reg_m = 0.82

    return round(effective_tier_m,3), round(effective_reg_m,3)


def scrape_player_multi():

    for index, row in players_df.iterrows():
        print(f"Scraping player {row['name']}")
        url = row['url']
        print(url)

        if url and not (isinstance(url, float) and math.isnan(url)):
            tiers, regions, opponents1 = get_opponents_tier_and_region(url)
            tiers2, regions2, opponents2 = get_opponents_tier_and_region(f"{url}/?page=2")
            tiers3, regions3, opponents3 = get_opponents_tier_and_region(f"{url}/?page=3")
        else:
            tiers, regions = [], []
            tiers2, regions2 = [], []
            tiers3, regions3 = [], []

        opponents = opponents1 + opponents2 + opponents3
        tiers = tiers + tiers2 + tiers3
        regions = regions + regions2
        effective_tier_m, effective_reg_m = get_tier_region_multi(tiers, regions)

        players_df.loc[index, 'tier_m'] = effective_tier_m
        players_df.loc[index, 'region_m'] = effective_reg_m
        
        player_name = row['name']
        players_90_df = pd.read_csv("player_data_90d.csv")
        player_data_all = pd.read_csv("player_data_all.csv")

        players_90_df['tier_m'] = players_90_df['tier_m'].astype(float)
        players_90_df['region_m'] = players_90_df['region_m'].astype(float)
        player_data_all['tier_m'] = player_data_all['tier_m'].astype(float)
        player_data_all['region_m'] = player_data_all['region_m'].astype(float)

        if player_name in players_90_df['Player'].values:
            players_90_df.loc[players_90_df['Player'] == player_name, 'tier_m'] = effective_tier_m
            players_90_df.loc[players_90_df['Player'] == player_name, 'region_m'] = effective_reg_m
        else:
            print(f"Player {player_name} not found in players_90_df.")
        players_90_df.to_csv("player_data_90d.csv", index=False)

        if player_name in player_data_all['Player'].values:
            player_data_all.loc[player_data_all['Player'] == player_name, 'tier_m'] = effective_tier_m
            player_data_all.loc[player_data_all['Player'] == player_name, 'region_m'] = effective_reg_m
            if "opponents" not in player_data_all.columns:
                player_data_all['opponents'] = None
            player_data_all.loc[player_data_all['Player'] == player_name, 'opponents'] = player_data_all.loc[
                player_data_all['Player'] == player_name, 'opponents'
            ].apply(lambda x: opponents)
        else:
            print(f"Player {player_name} not found in player_data_all.")
        player_data_all.to_csv("player_data_all.csv", index=False)
        
        players_df.drop_duplicates(subset=['url'], keep='last', inplace=True)

        players_df.to_csv("players.csv", index=False)
        print(effective_tier_m, effective_reg_m)
        time.sleep(random.uniform(0.5, 1.2))
        




