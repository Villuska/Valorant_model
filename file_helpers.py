import glob
import os
import pandas as pd
import datetime

def open_most_recent_csv(df_name: str, folder_name: str = "teams_elo_history") -> tuple[pd.DataFrame, str]:
    file_pattern = os.path.join(folder_name, f"{df_name}_*.csv")
    matching_files = glob.glob(file_pattern)

    if not matching_files:
        raise FileNotFoundError(f"No files found matching the pattern: {file_pattern}")

    most_recent_file = max(matching_files, key=lambda x: datetime.datetime.strptime(x[len(folder_name)+len(df_name)+2:-4], '%Y-%m-%d'))
    most_recent_date = most_recent_file[len(folder_name)+len(df_name)+2:-4]
    most_recent_date = datetime.datetime.strptime(most_recent_date, '%Y-%m-%d')
    # Load the most recent file into a DataFrame
    df = pd.read_csv(most_recent_file)

    return df

def save_df_as_csv(df: pd.DataFrame, df_name: str, folder_name: str = "teams_elo_history") -> None:

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    todays_date = datetime.datetime.today().strftime('%Y-%m-%d')
    
    filename = f"{df_name}_{todays_date}.csv"
    
    full_path = os.path.join(folder_name, filename)
    
    if os.path.exists(full_path):
        os.remove(full_path)
    
    df.to_csv(full_path, encoding='utf-8', index=False)

def open_csv_before_date(df_name: str, target_date: str, folder_name: str = "firepower_history") -> tuple[pd.DataFrame, str]:
    """
    Opens the most recent CSV file of df_name in folder_name that is before the supplied target_date.
    If no such file exists, opens the oldest available file instead.

    :param df_name: Name prefix of the CSV files to look for.
    :param target_date: The cutoff date in YYYY-MM-DD format. Fetches the file dated strictly before this date.
    :param folder_name: The folder where the CSV files are located.
    :return: A tuple of the DataFrame and the date string of the selected file.
    """
    import os
    import glob
    import pandas as pd
    from datetime import datetime

    # Generate the file pattern to find matching CSVs
    file_pattern = os.path.join(folder_name, f"{df_name}_*.csv")
    matching_files = glob.glob(file_pattern)

    if not matching_files:
        raise FileNotFoundError(f"No files found matching the pattern: {file_pattern}")

    # Parse the target date
    target_datetime = datetime.strptime(target_date, '%Y-%m-%d')

    # Filter files by their embedded date
    dated_files = [
        (datetime.strptime(file[len(folder_name)+len(df_name)+2:-4], '%Y-%m-%d'), file)
        for file in matching_files
    ]

    if not dated_files:
        raise FileNotFoundError(f"No valid files found with date format in the pattern: {file_pattern}.")

    # Separate files into those before the target date and others
    files_before_target = [(date, file) for date, file in dated_files if date < target_datetime]

    if files_before_target:
        # Get the most recent file before the target date
        selected_date, selected_file = max(files_before_target, key=lambda x: x[0])
    else:
        # If no files before the target date, choose the oldest available file
        selected_date, selected_file = min(dated_files, key=lambda x: x[0])

    # Load the selected file into a DataFrame
    df = pd.read_csv(selected_file)

    return df, selected_date.strftime('%Y-%m-%d'), target_date