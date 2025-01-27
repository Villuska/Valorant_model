import pandas as pd

df = pd.read_csv("valorant_team_strengths.csv")

df = df.applymap(lambda x: x.replace('"', '') if isinstance(x, str) else x)

df.to_csv("valorant_team_strengths.csv")