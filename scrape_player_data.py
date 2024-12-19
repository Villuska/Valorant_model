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

pd.set_option('mode.chained_assignment', None)

def find_player_data(url, timeframe):
    print(f"Scraping: {url}")

    player_stats_scraper_page = requests.get(url)
    player_stats_scraper_page = BeautifulSoup(player_stats_scraper_page.content, 'html.parser')
    
    player_stats = [elem.text for elem in player_stats_scraper_page.select("td+.mod-right, td.mod-center")]
    
    player_name = [elem.text for elem in player_stats_scraper_page.select(".wf-title")][0].strip()
    
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
        df.loc[:, 'url'] = url  # This avoids SettingWithCopyWarning
        
    else:
        columns = ["Player", "Team", "Rating", "ACS", "KD", "ADR", "KAST", "KPR", "APR", "FKPR", "FDPR", "Total_Rounds_Played"]
        df = pd.DataFrame([[player_name, team_name] + [0] * (len(columns) - 2)], columns=columns)

    if os.path.exists(f"player_data_{timeframe}.csv"):
        df.to_csv(f"player_data_{timeframe}.csv", header=False, mode='a', index=False)
        df = pd.read_csv(f"player_data_{timeframe}.csv")
        df = df.drop_duplicates(subset=['url'], keep='first', inplace=False)
        print(df)
        print("")
    else:
        df.to_csv(f"player_data_{timeframe}.csv", index=False)
        print(df)
        print("")
    
def main():
    base_urls_all = list(pd.read_csv("players.csv")['url'])
    for url in base_urls_all:
        find_player_data(url, 'all')
    base_urls_90 = list(pd.read_csv("players.csv")['url_90d'])
    for url in base_urls_90:
        find_player_data(url, '90d')

if __name__ == "__main__":
    main()