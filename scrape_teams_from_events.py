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


def get_tournaments():
    url = "https://www.vlr.gg/events"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.find_all('div', class_="events-container-col")[0]
        urls = set()
        for a_tag in element.find_all('a'):
            href = a_tag['href']
            if "/event/" in href:
                href = "https://www.vlr.gg/" + href
                urls.add(href)
        return list(urls)

def get_event_teams():
    
    event_urls = get_tournaments()
    team_urls = set()
    time.sleep(2)

    for url in event_urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                element = soup.find_all('div', class_="event-teams-container")[0]
                for a_tag in element.find_all('a'):
                    href = a_tag.get('href')
                    if href and "/team/" in href:
                        href = "https://www.vlr.gg" + href
                        team_urls.add(href)
                time.sleep(random.uniform(1,2))
            except IndexError:
                continue

    if os.path.exists("team_links.csv"):
        existing_urls = set(pd.read_csv("team_links.csv")['url'])
        all_urls = list(team_urls | existing_urls)
        df = pd.DataFrame({"url": all_urls})
        df.to_csv("team_links.csv", index=False)
    else:
        team_urls = list(team_urls)
        df = pd.DataFrame({"url": team_urls})
        df.to_csv("team_links.csv", index=False)        

   

get_event_teams()
