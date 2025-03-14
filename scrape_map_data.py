import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from datetime import datetime


def score_difference(score):
    team1, team2 = map(int, score.split('-'))
    return (team1 - team2)

def clean_team_name(name):
    return re.sub(r"\s*\[.*?\]\s*", "", name).strip()

def get_pistols_and_rounds(game_stats):

    titles = [
        div.get('title') for div in game_stats.find('div', class_='vlr-rounds-row').find_all('div', class_='vlr-rounds-row-col')
        if div.get('title')  # Ensuring it has a title attribute
    ]
    pistols_1 = 0
    pistols_2 = 0
    pistol_1 = titles[0].split("-")[0]
    if pistol_1 == "0":
        pistols_2 += 1
    else:
        pistols_1 += 1
    diff_12 = score_difference(titles[12])
    diff_13 = score_difference(titles[13])
    if diff_13 > diff_12:
        pistols_1 += 1
    else:
        pistols_2 += 1
    return titles, pistols_1, pistols_2


def handle_bo_x(game_stats, team_1, team_2, date, maps_played):
    team_1 = clean_team_name(team_1)
    team_2 = clean_team_name(team_2)
    match_df = pd.DataFrame()
    for i in range(len(game_stats)):
        if i != 1:
            
            table = game_stats[i].select("table")[0]  
            team_1_map_1 = hande_team_stats_table(table, "team_1_")
            table = game_stats[i].select("table")[1]
            team_2_map_1 = hande_team_stats_table(table, "team_2_")
            rounds, pistols_1, pistols_2 = get_pistols_and_rounds(game_stats[i])
            map_df = combine_and_clean_team_stats(team_1_map_1, team_2_map_1, team_1, team_2, date)
            map_df['team_1_pistols'] = pistols_1
            map_df['team_2_pistols'] = pistols_2
            map_df['rounds_prog'] = [rounds]
            match_df = pd.concat([match_df, map_df], ignore_index=True)


    match_df['map'] = maps_played
    return match_df

def combine_and_clean_team_stats(team_1_stats, team_2_stats, team_1, team_2, date):

    df_combined = pd.concat([team_1_stats, team_2_stats], axis=1)
    df_combined.insert(0, 'date', date)
    df_combined.insert(0, 'team_2', team_2)
    df_combined.insert(0, 'team_1', team_1)
    return df_combined

def hande_team_stats_table(table, team):
    # Extract table headers (if present), cleaning unwanted characters
    try:
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
        #print(df)
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
            'R2.0': 'rating',
            '+/–_0': 'KD_diff',
            '+/–_1': 'op_diff'
        })
        df = df.drop(columns=['rating', 'HS%'])
        df = df.apply(pd.to_numeric, errors='coerce')
        average_row = df.mean()
        average_row = average_row.dropna()
        df_averages = pd.DataFrame([average_row], columns=average_row.index)
        df_averages.columns = [team + col for col in df_averages.columns]

        return df_averages
    except Exception as e:
        return pd.DataFrame()

def game_stats_scraping_function(url):
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
   


    game_stats = soup.select(".vm-stats-game")
    maps_played = soup.find('div', class_='vm-stats-gamesnav-container').text.replace("\t", "").replace("\n", "")
    maps_played = maps_played.replace("All Maps", "")
    split_list = re.split(r'\d+', maps_played)  # Split by one or more digits
    # Step 3: Remove any empty strings from the list (if any)
    maps_played = [item for item in split_list if item]


    match_df = handle_bo_x(game_stats, team_1, team_2, date, maps_played)
    cols = match_df.columns.tolist()  # Get the current column order
    cols.remove("map")  # Remove "map" from its current position
    cols.insert(2, "map")  # Insert "map" at the third position

    # Reorder the DataFrame
    match_df = match_df[cols]

    print(match_df)
    return match_df


df = game_stats_scraping_function("https://www.vlr.gg/429390/team-vitality-vs-team-liquid-champions-tour-2025-emea-kickoff-gf")
df.to_csv("example_match_data.csv", index=False)

"""ota mapin rundit silleen et numbers = rundit ja sit tee loppuun"""