import pandas as pd
import numpy as np

def clean_data(df):
    """
    Removes 'Empty Net' situations which distort defensive stats.
    """
    clean_df = df[
        (df['home_off_line'] != 'empty_net_line') & 
        (df['away_off_line'] != 'empty_net_line')
    ].copy()
    return clean_df

def calculate_special_teams(df):
    """
    Calculates Power Play (PP) efficiency using xG per 60 minutes.
    """
    pp_df = df[df['home_off_line'] == 'PP_up']
    pp_stats = pp_df.groupby('home_team')[['home_xg', 'toi']].sum().reset_index()
    # Normalise by Time on Ice (per 60 mins)
    pp_stats['pp_efficiency'] = (pp_stats['home_xg'] / pp_stats['toi']) * 3600
    return pp_stats[['home_team', 'pp_efficiency']].rename(columns={'home_team': 'team'})

def calculate_discipline(df):
    """
    Calculates Discipline based on Penalty Minutes (PIM).
    """

    home_penalties = df.groupby('home_team')['home_penalty_minutes'].sum().reset_index()
    away_penalties = df.groupby('away_team')['away_penalty_minutes'].sum().reset_index()
    
    home_penalties.columns = ['team', 'pim']
    away_penalties.columns = ['team', 'pim']
    total_pim = pd.concat([home_penalties, away_penalties]).groupby('team').sum().reset_index()
    
    return total_pim

def calculate_features(df):
    df_clean = clean_data(df)

    home_stats = df_clean.groupby("home_team")[
        ["home_xg", "away_xg", "home_goals", "away_goals", "home_shots", "away_shots"]
    ].sum().reset_index()
    home_stats.columns = ["team", "xg_for", "xg_against", "goals_for", "goals_against", "shots_for", "shots_against"]

    away_stats = df_clean.groupby("away_team")[
        ["away_xg", "home_xg", "away_goals", "home_goals", "away_shots", "home_shots"]
    ].sum().reset_index()
    away_stats.columns = ["team", "xg_for", "xg_against", "goals_for", "goals_against", "shots_for", "shots_against"]

    season_stats = pd.concat([home_stats, away_stats]).groupby("team").sum().reset_index()

    season_stats["GSAx"] = season_stats["xg_against"] - season_stats["goals_against"]
    
    pp_stats = calculate_special_teams(df)
    discipline_stats = calculate_discipline(df)
    
    season_stats = season_stats.merge(pp_stats, on='team', how='left').fillna(0)
    season_stats = season_stats.merge(discipline_stats, on='team', how='left').fillna(0)

    
    season_stats['raw_off_score'] = (0.4 * season_stats['xg_for']) + \
                                    (0.4 * season_stats['goals_for']) + \
                                    (0.2 * season_stats['shots_for'])
                                    
    season_stats['raw_def_score'] = (0.4 * season_stats['xg_against']) + \
                                    (0.4 * season_stats['goals_against']) + \
                                    (0.2 * season_stats['shots_against'])


    season_stats['adj_off_score'] = season_stats['raw_off_score'] + (season_stats['pp_efficiency'] * 10)
    

    season_stats['adj_def_score'] = season_stats['raw_def_score'] * (1 + (season_stats['pim'] / 5000))

    return season_stats

def calc_win_pct(stats_df):
    """
    Calculates Pythagorean Win % using the Adjusted Composite Scores.
    """
    exponent = 2.15 
    
    stats_df['win_pct'] = (stats_df['adj_off_score'] ** exponent) / \
                          ((stats_df['adj_off_score'] ** exponent) + 
                           (stats_df['adj_def_score'] ** exponent))
                           
    return stats_df.sort_values('win_pct', ascending=False)