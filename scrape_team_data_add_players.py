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

def add_players_to_csv(player_tuple):
    name = player_tuple[0]
    url = player_tuple[1]
    if not "?timespan=all" in url:
        url = url + "?timespan=all"

    url_90 = url + "/?timespan=90d"
    columns = ['name', 'url', 'url_90d']
    if os.path.exists("players.csv"):
        if url not in pd.read_csv("players.csv")['url']:
            df = pd.DataFrame(columns=columns, data=[[name, url, url_90]])
            df.to_csv("players.csv", header=False, mode='a', index=False)
    else:
        df = pd.DataFrame(columns=columns, data=[[name, url, url_90]])
        df.to_csv("players.csv", index=False)

def get_players_from_soup(soup):
    player_urls = []
    players = []
    elements = soup.find_all('div', class_="team-roster-item")
    for element in elements:
        e_text = element.text.replace("\n", "")
        for i in e_text.split("\t"):
            if not "analyst" in e_text.split("\t") and not "head coach" in e_text.split("\t"):
                if i != "":
                    players.append(i)
                    break
    for element in elements[:len(players)]:
        for a_tag in element.find_all('a'):
            href = a_tag['href']
            if "/player/" in href:
                href = "https://www.vlr.gg" + href
                player_urls.append(href)

    combined_list = list(zip(players, player_urls))
    for i in combined_list:
        add_players_to_csv(i)
    return players

def get_team_data_from_soup(soup):
    pass

def get_last_change(url):
    pass


def get_team_data_and_add_players(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        players = get_players_from_soup(soup)
        
get_team_data_and_add_players("https://www.vlr.gg/team/16898/trust-in-plug")