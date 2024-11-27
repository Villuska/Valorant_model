
import pandas as pd
import unicodedata
"""
tee ekaks helpperi et saa noi vitun tiimien nimet fiksummiks
"""
def normify_team_name(team):
    team = team.lower()
    # Replace spaces with hyphens
    team = team.replace(" ", "-")
    # Normalize to ASCII
    team = unicodedata.normalize('NFD', team).encode('ascii', 'ignore').decode('utf-8')
    # Keep only alphanumeric characters and hyphens
    result = "".join([char for char in team if char.isalnum() or char == '-'])
    return result

def form_team_url_guess(row):
    url = f"https://www.vlr.gg/team/{row['team']}/{row['id']}"
    return url

