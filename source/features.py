import pandas as pd
import numpy as np

WEIGHT_GOALS = 0.4
WEIGHT_XG = 0.4
WEIGHT_SHOTS = 0.2

PP_WEIGHT = 50 

PIM_FACTOR = 5000 

def clean_data(df):
    clean_df = df[
        (df["home_off_line"] != "empty_net_line") & 
        (df["away_off_line"] != "empty_net_line")
    ].copy()
    return clean_df

def calculate_special_teams(df):
    home_pp = df[df["home_off_line"] == "PP_up"].groupby("home_team")[
        ["home_xg", "toi"]
    ].sum().reset_index()
    home_pp.columns = ["team", "xg", "toi"]

    away_pp = df[df["away_off_line"] == "PP_up"].groupby("away_team")[
        ["away_xg", "toi"]
    ].sum().reset_index()
    away_pp.columns = ["team", "xg", "toi"]
    total_pp = pd.concat([home_pp, away_pp]).groupby("team").sum().reset_index()

    total_pp["pp_efficiency"] = np.where(
        total_pp["toi"] > 0, 
        (total_pp["xg"] / total_pp["toi"]) * 3600, 
        0
    )
    
    return total_pp[["team", "pp_efficiency"]]

def calculate_discipline(df):
    home_penalties = df.groupby("home_team")["home_penalty_minutes"].sum().reset_index()
    away_penalties = df.groupby("away_team")["away_penalty_minutes"].sum().reset_index()
    
    home_penalties.columns = ["team", "pim"]
    away_penalties.columns = ["team", "pim"]
    total_pim = pd.concat([home_penalties, away_penalties]).groupby("team").sum().reset_index()
    return total_pim

def calculate_features(df):
    df_clean = clean_data(df)

    home_stats = df_clean.groupby("home_team")[
        ["home_xg", "away_xg", "home_goals", "away_goals", "home_shots", "away_shots", "toi"]
    ].sum().reset_index()
    home_stats.columns = ["team", "xg_for", "xg_against", "goals_for", "goals_against", "shots_for", "shots_against", "toi"]

    away_stats = df_clean.groupby("away_team")[
        ["away_xg", "home_xg", "away_goals", "home_goals", "away_shots", "home_shots", "toi"]
    ].sum().reset_index()
    away_stats.columns = ["team", "xg_for", "xg_against", "goals_for", "goals_against", "shots_for", "shots_against", "toi"]

    season_stats = pd.concat([home_stats, away_stats]).groupby("team").sum().reset_index()

    season_stats["GSAx"] = season_stats["xg_against"] - season_stats["goals_against"]
    
    pp_stats = calculate_special_teams(df)
    discipline_stats = calculate_discipline(df)
    
    season_stats = season_stats.merge(pp_stats, on="team", how="left").fillna(0)
    season_stats = season_stats.merge(discipline_stats, on="team", how="left").fillna(0)

    season_stats["raw_off_total"] = (WEIGHT_XG * season_stats["xg_for"]) + \
                                    (WEIGHT_GOALS * season_stats["goals_for"]) + \
                                    (WEIGHT_SHOTS * season_stats["shots_for"])
                                    
    season_stats["raw_def_total"] = (WEIGHT_XG * season_stats["xg_against"]) + \
                                    (WEIGHT_GOALS * season_stats["goals_against"]) + \
                                    (WEIGHT_SHOTS * season_stats["shots_against"])

    season_stats["toi_hours"] = season_stats["toi"] / 3600
    
    season_stats["raw_off_rate"] = season_stats["raw_off_total"] / season_stats["toi_hours"]
    season_stats["raw_def_rate"] = season_stats["raw_def_total"] / season_stats["toi_hours"]

    season_stats["adj_off_score"] = season_stats["raw_off_rate"] * (1 + (season_stats["pp_efficiency"] / PP_WEIGHT))

    season_stats["adj_def_score"] = season_stats["raw_def_rate"] * (1 + (season_stats["pim"] / PIM_FACTOR))

    return season_stats

def calc_win_pct(stats_df):
    exponent = 2.15 
    
    stats_df["win_pct"] = (stats_df["adj_off_score"] ** exponent) / \
                          ((stats_df["adj_off_score"] ** exponent) + 
                           (stats_df["adj_def_score"] ** exponent))
                           
    return stats_df.sort_values("win_pct", ascending=False)