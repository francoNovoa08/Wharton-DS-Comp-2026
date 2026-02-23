# Given by 0.56 / (1 - 0.56) for a +6% home team advantage
HOME_ADVANTAGE_MULTIPLIER = 1.27

def predict_matchup(home_team, away_team, rankings_df):
    p_home = rankings_df.loc[home_team, "win_pct"]
    p_away = rankings_df.loc[away_team, "win_pct"]
    
    p_home = max(0.001, min(0.999, p_home))
    p_away = max(0.001, min(0.999, p_away))
        
    numerator = p_home * (1 - p_away)
    denominator = numerator + (p_away * (1 - p_home))
    raw_prob = numerator / denominator

    raw_prob = max(0.001, min(0.999, raw_prob))

    current_odds = raw_prob / (1 - raw_prob)
    new_odds = current_odds * HOME_ADVANTAGE_MULTIPLIER

    final_prob = new_odds / (1 + new_odds)
        
    return final_prob