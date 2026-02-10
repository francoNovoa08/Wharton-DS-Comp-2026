def predict_matchup(home_team, away_team, rankings_df):
    p_home = rankings_df.loc[home_team, "win_pct"]
    p_away = rankings_df.loc[away_team, "win_pct"]

    num = p_home * (1 - p_away)
    denom = (p_home * (1 - p_away)) + (p_away * (1 - p_home))

    return num / denom