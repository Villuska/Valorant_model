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
from get_regions_from_old import *

def add_players_to_csv(player_tuple, team):
    name = player_tuple[0]
    url = player_tuple[1]
    if not "?timespan=all" in url:
        url = url + "?timespan=all"

    url_90 = url + "/?timespan=90d".replace("?timespan=all/", "?timespan=90d")
    columns = ['name', 'team', 'url', 'url_90d', 'tier_m', 'region_m']
    if os.path.exists("players.csv"):
        if url not in pd.read_csv("players.csv")['url']:
            df = pd.DataFrame(columns=columns, data=[[name, team, url, url_90, None, None]])
            df.to_csv("players.csv", header=False, mode='a', index=False)
    else:
        df = pd.DataFrame(columns=columns, data=[[name, team, url, url_90, None, None]])
        df.to_csv("players.csv", index=False)

def get_players_from_soup(soup, team):
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
        add_players_to_csv(i, team)
    return players

def get_team_data_from_soup(soup):
    abrrevation = None
    name = None
    try:
        name = soup.find_all('h1', class_="wf-title")[0].text
    except IndexError:
        name = None
    try:
        abrrevation = soup.find_all('h2', class_="wf-title team-header-tag")[0].text
    except IndexError:
        abrrevation = None
    return name, abrrevation

def get_last_change(url):
    url = url.replace("/team/", "/team/transactions/")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find_all('table', class_="wf-faux-table")[0]
            # If you want to extract rows from the table
        rows = table.find_all('tr')
        trans_list = []
        for row in rows:
            # Extract cells (td or th) from the row
            cells = row.find_all(['td', 'th'])
            cell_data = [cell.text.strip().replace("\t", "") for cell in cells]
            trans_list.append(cell_data)
        data = trans_list[1:]
        try:
            first_date = data[0][0]
            count = sum(1 for inner_list in data if inner_list[0] == first_date and inner_list[4] == 'Player')
            first_date = first_date.replace("/", "-")
        except IndexError:
            first_date = "2024-06-06"
            count = 0
        return first_date, count
    else:
        return "2024-06-06", 0

    

def get_team_data_and_add_players(url):
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        name, abbrevation = get_team_data_from_soup(soup)
        players = get_players_from_soup(soup, name)
        last_change, changes = get_last_change(url)
        region = None
        tier = None
        columns = ['team', 'abbrevation', 'region', 'tier','players', 'last_change', 'changes', 'url']
        if os.path.exists("teams.csv"):
            if url not in pd.read_csv("teams.csv")['url'].tolist():
                df = pd.DataFrame(columns=columns, data=[[name, abbrevation, region, tier, players, last_change, changes, url]])
                print("")
                df.to_csv("teams.csv", header=False, mode='a', index=False)
                print(df)
                print("")
        else:
            df = pd.DataFrame(columns=columns, data=[[name, abbrevation, region, tier, players, last_change, changes, url]])
            df.to_csv("teams.csv", index=False)
            print("")
            print(df)
            print("")

def main():
    urls = list(pd.read_csv("team_links.csv")['url'])
    existing_urls = pd.read_csv("teams.csv")['url'].tolist()
    urls = list(set(urls) - set(existing_urls))
    for url in urls:     
        get_team_data_and_add_players(url)
    print("")
    print("Scraping done!")
    print("")
    get_regions_from_old()

if __name__ == "__main__":
    main()