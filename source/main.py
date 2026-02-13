import pandas as pd
import features
import predict
import line_performance

df = pd.read_csv("whl_2025.csv")
# --- PHASE 1a: Team Performance ---
team_stats = features.calculate_features(df)
power_rankings = features.calc_win_pct(team_stats)
power_rankings.set_index("team", inplace=True)

print("\n--- POWER RANKINGS ---")
print(f"{"Rank":<5} {"Team":<25} {"Win Pct":<10}")
power_rankings["rank"] = range(1, len(power_rankings) + 1)

for team, row in power_rankings.iterrows():
    print(f"#{row["rank"]:<4} {team:<25} {row["win_pct"]:.4f}")

matchups = pd.read_csv("matchups.csv")
print("\n--- MATCHUP PREDICTIONS ---")
for index, row in matchups.iterrows():
    home = row["home_team"]
    away = row["away_team"]
    prob = predict.predict_matchup(home, away, power_rankings)
    print(f"Game {row["game"]}: {home} vs {away} -> {prob:.1%} Home Win")

# --- PHASE 1b: Line Disparity ---
analyser = line_performance.LinePerformanceAnalyser("whl_2025.csv")
line_stats = analyser.analyse()
disparity = analyser.get_disparity(line_stats)

print("\n--- TOP 10 LINE DISPARITY ---")
print(f"{"Rank":<5} {"Team":<25} {"Ratio":<10} {"L1 Adj xG":<10} {"L2 Adj xG":<10}")

for i, (team, row) in enumerate(disparity.head(10).iterrows(), 1):
    print(f"#{i:<4} {team:<25} {row["Disparity_Ratio"]:.3f}      {row["Line_1_Adj"]:.2f}       {row["Line_2_Adj"]:.2f}")

