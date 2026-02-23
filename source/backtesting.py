import pandas as pd
import features
import predict

df = pd.read_csv("whl_2025.csv")
team_stats = features.calculate_features(df)
power_rankings = features.calc_win_pct(team_stats)
power_rankings.set_index("team", inplace=True)

games = df.groupby(['game_id', 'home_team', 'away_team'])[['home_goals', 'away_goals']].sum().reset_index()

correct_predictions = 0
total_games = 0
ties = 0

for index, row in games.iterrows():
    home_team = row['home_team']
    away_team = row['away_team']
    home_goals = row['home_goals']
    away_goals = row['away_goals']
    
    if home_goals == away_goals:
        ties += 1
        continue
        
    total_games += 1
    
    actual_home_win = 1 if home_goals > away_goals else 0
    
    prob_home_win = predict.predict_matchup(home_team, away_team, power_rankings)
    predicted_home_win = 1 if prob_home_win > 0.5 else 0
    
    if actual_home_win == predicted_home_win:
        correct_predictions += 1

accuracy = correct_predictions / total_games

print(f"Total games evaluated: {total_games}")
print(f"Correct predictions: {correct_predictions}")
print(f"Model Accuracy: {accuracy:.2%}")