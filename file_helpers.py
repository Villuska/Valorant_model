import glob
import os
import pandas as pd
import datetime

def open_most_recent_csv(df_name: str, folder_name: str = "teams_elo_history") -> tuple[pd.DataFrame, str]:
    file_pattern = os.path.join(folder_name, f"{df_name}_*.csv")
    matching_files = glob.glob(file_pattern)

    if not matching_files:
        raise FileNotFoundError(f"No files found matching the pattern: {file_pattern}")

    most_recent_file = max(matching_files, key=lambda x: datetime.strptime(x[len(folder_name)+len(df_name)+2:-4], '%Y-%m-%d'))
    most_recent_date = most_recent_file[len(folder_name)+len(df_name)+2:-4]
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    # Load the most recent file into a DataFrame
    df = pd.read_csv(most_recent_file)

    return df

def save_df_as_csv(df: pd.DataFrame, df_name: str, folder_name: str = "teams_elo_history") -> None:

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    todays_date = datetime.today().strftime('%Y-%m-%d')
    
    filename = f"{df_name}_{todays_date}.csv"
    
    full_path = os.path.join(folder_name, filename)
    
    if os.path.exists(full_path):
        os.remove(full_path)
    
    df.to_csv(full_path, encoding='utf-8', index=False)

