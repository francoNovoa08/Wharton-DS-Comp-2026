import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import predict

df = pd.read_csv("whl_2025.csv")
game_stats = df.groupby(["game_id", "home_team", "away_team"])[["home_goals", "away_goals", "home_xg", "away_xg"]].sum().reset_index()

home_df = game_stats[["game_id", "home_team", "home_xg", "away_xg", "home_goals", "away_goals"]].copy()
home_df.columns = ["game_id", "team", "xg_for", "xg_against", "goals_for", "goals_against"]
home_df["is_home"] = 1

away_df = game_stats[["game_id", "away_team", "away_xg", "home_xg", "away_goals", "home_goals"]].copy()
away_df.columns = ["game_id", "team", "xg_for", "xg_against", "goals_for", "goals_against"]
away_df["is_home"] = 0

team_logs = pd.concat([home_df, away_df])

season_stats = team_logs.groupby("team")[["xg_for", "xg_against"]].sum()
season_stats["win_pct"] = (season_stats["xg_for"]**2) / \
                                 (season_stats["xg_for"]**2 + season_stats["xg_against"]**2)

power_rankings = season_stats.sort_values("win_pct", ascending=False)
print("Top 5 Teams by Power Ranking:")
print(power_rankings.head())