def predict_matchup(home_team, away_team, rankings_df):
    p_home = rankings_df.loc[home_team, "win_pct"]
    p_away = rankings_df.loc[away_team, "win_pct"]
        
    numerator = p_home * (1 - p_away)
    denominator = (p_home * (1 - p_away)) + (p_away * (1 - p_home))
    raw_prob = numerator / denominator

    home_advantage = 0.06

    final_prob = min(raw_prob + home_advantage, 0.99)
        
    return final_prob