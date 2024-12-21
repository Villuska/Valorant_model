import pandas as pd

def get_regions_from_old():
    old_df = pd.read_csv("valorant_team_strengths.csv")
    new_df = pd.read_csv("teams.csv")
    columns = ['team', 'abbrevation', 'region', 'tier','players', 'last_change', 'changes', 'url']
    old_df_teams = list(old_df['Team'])

    list_of_rows = []

    for index, row in new_df.iterrows():
        if not row['team'] in old_df_teams:
            row['region'] = None
            row['tier'] = None
            list_of_rows.append(row)
        else:
            old_row = old_df[old_df['Team'] == row['team']]
            row['tier'] = old_row['Tier'].values[0]
            row['region'] = old_row['Region'].values[0]
            list_of_rows.append(row)

    df = pd.DataFrame(data=list_of_rows, columns=columns)
    df.to_csv("teams.csv", index=False)