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
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import os
import time
from scipy.interpolate import interp1d
import itertools
import math
from scrape_player_multi import *
from file_helpers import *
from form_initial_strengths import *
from form_player_strengths import *
pd.set_option('mode.chained_assignment', None)

def find_player_data(url, timeframe):
    if timeframe == "90d":
        url = url.replace("?timespan=all/", "?timespan=90d").replace("?timespan=all", "?timespan=90d")
        last_occurrence = url.rfind("?timespan=90d")
        if last_occurrence != -1 and url.count("?timespan=90d") > 1:
            url = url[:last_occurrence] + url[last_occurrence + len("?timespan=90d"):]
    print(f"Scraping: {url}")
    
    tries = 0
    max_tries = 100
    while tries < max_tries:
        try:
            player_stats_scraper_page = requests.get(url)
            player_stats_scraper_page = BeautifulSoup(player_stats_scraper_page.content, 'html.parser')
            player_stats = [elem.text for elem in player_stats_scraper_page.select("td+.mod-right, td.mod-center")]
            
            player_name = [elem.text for elem in player_stats_scraper_page.select(".wf-title")][0].strip()
            break
        except Exception as e:
            tries += 1
            if tries == max_tries:
                player_name = None
            time.sleep(random.uniform(tries+0.5,tries+1))
            
   
    
    team_name = requests.get(url)
    team_name = BeautifulSoup(team_name.content, 'html.parser')
    try:
        team_name = team_name.select_one("div[style='font-weight: 500;']").text.strip()
    except Exception as e:
        print(e)
        team_name = None
    
    num_rows = int(len(player_stats)/16)
    if num_rows != 0:

        # Reshape and create DataFrame
        player_stats_table = np.array(player_stats).reshape(num_rows, 16)
        player_stats_table = pd.DataFrame(player_stats_table)
        player_stats_table.columns = ["Use","Rounds_Played","Rating","ACS","KD","ADR","KAST","KPR","APR","FKPR","FDPR","K","D","A","FK","FD"]
        
        # Drop 'Use' column
        player_stats_table = player_stats_table.drop(columns=["Use"])

        # Remove '%' from 'KAST' and convert columns to numeric
        player_stats_table["KAST"] = player_stats_table["KAST"].str.replace("%", "")
        player_stats_table = player_stats_table.apply(pd.to_numeric, errors='coerce').dropna()
        
        # Calculate total rounds played
        Total_Rounds_Played = player_stats_table["Rounds_Played"].sum()

        # Normalize 'KAST'
        player_stats_table["KAST"] = player_stats_table["KAST"] / 100
        print(player_stats_table)
        # Add 'Total_Rounds_Played' column
        player_stats_table["Total_Rounds_Played"] = Total_Rounds_Played
        # Calculate 'Percentage_Rounds_Played'
        player_stats_table["Percentage_Rounds_Played"] = player_stats_table["Rounds_Played"] / Total_Rounds_Played

        player_stats_table = player_stats_table.mul(player_stats_table["Percentage_Rounds_Played"], axis=0)
        player_stats_table = player_stats_table.sum()
        player_stats_table = pd.DataFrame(player_stats_table).T
        
        player_stats_table["Player"] = player_name
        player_stats_table["Team"] = team_name
        
        # Using .loc to set the 'url' column
        df = player_stats_table[["Player", "Team", "Rating", "ACS", "KD", "ADR", "KAST", "KPR", "APR", "FKPR", "FDPR", "Total_Rounds_Played"]]
        columns_to_round = ["Rating", "ACS", "KD", "ADR", "KAST", "KPR", "APR", "FKPR", "FDPR", "Total_Rounds_Played"]
        df[columns_to_round] = df[columns_to_round].round(3)
        df.loc[:, 'url'] = url  # This avoids SettingWithCopyWarning
        
    else:
        columns = ["Player", "Team", "Rating", "ACS", "KD", "ADR", "KAST", "KPR", "APR", "FKPR", "FDPR", "Total_Rounds_Played"]
        df = pd.DataFrame([[player_name, team_name] + [0] * (len(columns) - 2)], columns=columns)

    df['tier_m'] = 0.85
    df['region_m'] = 0.85
    
    print(df)
    if os.path.exists(f"player_data_{timeframe}.csv"):
        print("")
        existing_df = pd.read_csv(f"player_data_{timeframe}.csv")
        updated_df = pd.concat([existing_df, df]).drop_duplicates(subset='url', keep='last')
        updated_df.to_csv(f"player_data_{timeframe}.csv", index=False)

    else:
        df.to_csv(f"player_data_{timeframe}.csv", index=False)
        print("")
    
def scrape_player_data():
    base_urls_90 = list(pd.read_csv("players.csv")['url_90d'].dropna())
    for url in base_urls_90:
        find_player_data(url, '90d')
        players_df_90 = pd.read_csv("player_data_90d.csv")
        save_df_as_csv(players_df_90, "player_data_90d", "past_player_data_90d")
    base_urls_all = list(pd.read_csv("players.csv")['url'].dropna())
    for url in base_urls_all:
        find_player_data(url, 'all')
        players_df_all = pd.read_csv("player_data_all.csv")
        save_df_as_csv(players_df_all, "player_data_all", "past_player_data_all")

        
    scrape_player_multi()
    
    

    form_player_strengths()
    form_initial_strengths()
    


