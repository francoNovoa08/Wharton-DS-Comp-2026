import pandas as pd
import features
import predict

df = pd.read_csv("whl_2025.csv")

team_stats = features.calculate_features(df)
power_rankings = features.calc_win_pct(team_stats)
power_rankings.set_index("team", inplace=True)

matchups = pd.read_csv("matchups.csv")
print("\n--- MATCHUP PREDICTIONS")

results = []
for index, row in matchups.iterrows():
    home = row['home_team']
    away = row['away_team']
    
    prob = predict.predict_matchup(home, away, power_rankings)
    
    print(f"Game {row['game']}: {home} vs {away} -> {prob:.4%} Home Win")
    results.append({'Game': row['game'], 'Home': home, 'Away': away, 'Prob': prob})
