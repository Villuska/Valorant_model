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
from datetime import datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import os
import time
from scipy.interpolate import interp1d
import itertools
import math

def hande_team_stats_table(table, team):
    # Extract table headers (if present), cleaning unwanted characters
    headers = [re.sub(r'\n\d+', '', th.text.replace('\t', '').replace('\n', '').strip()) for th in table.find_all('th')]

    # Extract table rows, cleaning unwanted characters
    rows = []
    for tr in table.find_all('tr'):
        cells = []
        for td in tr.find_all('td'):
            # Clean up the text by removing unnecessary newlines and tabs
            clean_text = td.text.replace('\t', ' ').replace('\n', ' ').strip()

            # Split by spaces, \n, or \t, and keep the first part if there are splits
            split_text = clean_text.split()  # This splits on any whitespace, including \n and \t

            # Keep only the first part (if there's more than one)
            if split_text:
                clean_text = split_text[0]

            cells.append(clean_text)

        # Only append non-empty rows
        if cells:
            rows.append(cells)

    # Create a DataFrame
    if headers:  # If headers exist, use them as column names
        df = pd.DataFrame(rows, columns=headers)
    else:  # Otherwise, just create the DataFrame without column names
        df = pd.DataFrame(rows)

    plus_minus_counter = 0

    # Rename '+/–' columns to make them unique
    new_columns = []
    for col in df.columns:
        if col == '+/–':
            new_columns.append(f"+/–_{plus_minus_counter}")
            plus_minus_counter += 1
        else:
            new_columns.append(col)

    # Update the DataFrame columns with the new names
    df.columns = new_columns

    # Check renamed column names
    
    df['R2.0'] = df['R2.0'].apply(lambda x: round(float('.'.join(x.split('.')[:2])), 2) if isinstance(x, str) else x)
    # ACS: Take first 3 digits
    df['ACS'] = df['ACS'].apply(lambda x: re.match(r'\d{1,3}', x).group() if re.match(r'\d{1,3}', x) else x)
    
    # K: Take first 2 digits
    df['K'] = df['K'].apply(lambda x: re.match(r'\d{1,2}', x).group() if re.match(r'\d{1,2}', x) else x)

    # D: Remove all '/' and take first 2 digits
    df['D'] = df['D'].apply(lambda x: re.sub(r'/', '', x)[:2])

    # A: Take first 2 digits
    df['A'] = df['A'].apply(lambda x: re.match(r'\d{1,2}', x).group() if re.match(r'\d{1,2}', x) else x)

    # KAST: Take everything before the first '%'
    df['KAST'] = df['KAST'].apply(lambda x: re.split(r'%', x)[0] if isinstance(x, str) else x)

    # ADR: Keep the first 3 digits
    df['ADR'] = df['ADR'].apply(lambda x: re.match(r'\d{1,3}', x).group() if re.match(r'\d{1,3}', x) else x)

    # HS%: Keep the first 3 digits
    df['HS%'] = df['HS%'].apply(lambda x: re.match(r'\d{1,3}', x).group() if re.match(r'\d{1,3}', x) else x)

    def keep_first_plus_or_minus(value):
        # Match the first '+' or '-' followed by the number
        match = re.match(r"([+-]\d+)", value)
        return match.group(1) if match else value

    # Apply logic to all renamed '+/–' columns
    for col in df.columns:
        if '+/–' in col:
            df[col] = df[col].apply(lambda x: keep_first_plus_or_minus(x) if isinstance(x, str) else x)
            # Print the DataFrame
    
    df['+/–_0'] = pd.to_numeric(df['+/–_0'], errors='coerce')  # This will convert invalid numbers to NaN
    df['K'] = pd.to_numeric(df['K'], errors='coerce')
    df.columns = new_columns
    # Calculate column 'D' based on the conditions
    df['D'] = df.apply(lambda row: row['K'] + abs(row['+/–_0']) if row['+/–_0'] < 0 else row['K'] - row['+/–_0'], axis=1)
    df = df.rename(columns={
        'R2.0': 'Rating',
        '+/–_0': 'KD_Diff',
        '+/–_1': 'Op_diff'
    })
    df = df.drop(columns='Rating')
    df = df.apply(pd.to_numeric, errors='coerce')
    average_row = df.mean()
    average_row = average_row.dropna()
    df_averages = pd.DataFrame([average_row], columns=average_row.index)
    df_averages.columns = [team + col for col in df_averages.columns]
    return df_averages

def scrape_match_data(url):
    match_page = requests.get(url)
    soup = BeautifulSoup(match_page.content, 'html.parser')

    score_text = soup.find('div', class_="match-header-vs-score").text.replace('\t', ' ').replace('\n', ' ').strip()
    numbers = re.findall(r'\d+', score_text)

    # Convert the extracted numbers to integers
    numbers = list(map(int, numbers))
    # Sum the numbers
    maps_played = sum(numbers[:-1])

    team_1 = soup.find('a', class_="match-header-link wf-link-hover mod-1").text.replace('\t', ' ').replace('\n', ' ').strip()
    team_2 = soup.find('a', class_="match-header-link wf-link-hover mod-2").text.replace('\t', ' ').replace('\n', ' ').strip()

    date_text = soup.find('div', class_="match-header-date").text.replace('\t', ' ').replace('\n', ' ').strip()
    match = re.search(r'(\w+),\s+(\w+)\s+(\d+)(?:th|st|nd|rd)', date_text)

    if match:
        month_str = match.group(2)
        day = int(match.group(3))

        # Get the current year
        current_year = datetime.now().year

        # Convert month name to month number
        month = datetime.strptime(month_str, "%B").month

        # Format the date in y-m-d format
        date = f"{current_year}-{month:02d}-{day:02d}"
    else:
        date = "2025-01-01"
    
    elements = soup.select('.vm-stats-gamesnav-item.js-map-switch')
    href_urls = []
    # Iterate through the elements and extract the data-href attribute
    for elem in elements:
        data_href = elem.get('data-href')
        href_urls.append(data_href)



    if len(href_urls) > 0:
        page = requests.get("https://www.vlr.gg"+href_urls[0])
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.findAll('table', class_='wf-table-inset mod-overview')[2]
        if table:
            team_1_stats = hande_team_stats_table(table, 'Team_1_')
            print(team_1_stats)

        table = soup.findAll('table', class_='wf-table-inset mod-overview')[3]
        if table:
            team_2_stats = hande_team_stats_table(table, 'Team_2_')
            print(team_2_stats)
    else:
        table = soup.findAll('table', class_='wf-table-inset mod-overview')[0]
        if table:
            team_1_stats = hande_team_stats_table(table, 'Team_1_')
            print(team_1_stats)

        table = soup.findAll('table', class_='wf-table-inset mod-overview')[1]
        if table:
            team_2_stats = hande_team_stats_table(table, 'Team_2_')
            print(team_2_stats)

    winner = team_1
    if numbers[1] > numbers[0]:
        winner = team_2
    df_combined = pd.concat([team_1_stats, team_2_stats], axis=1)
    df_combined.insert(0, 'Date', date)
    df_combined.insert(0, 'Team_2_Score', numbers[1])
    df_combined.insert(0, 'Team_1_Score', numbers[0])
    df_combined.insert(0, 'Winner', winner)
    df_combined.insert(0, 'Maps_Played', maps_played)
    df_combined.insert(0, 'Team_2', team_2)
    df_combined.insert(0, 'Team_1', team_1)
    df_combined.to_csv("test.csv", index=False)

scrape_match_data("https://www.vlr.gg/433489/mandatory-vs-joblife-challengers-league-2025-france-revolution-split-1-w3/?game=all&tab=overview")