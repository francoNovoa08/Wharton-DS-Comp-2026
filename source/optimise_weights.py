import pandas as pd
import features
import predict

df = pd.read_csv("whl_2025.csv")
games = df.groupby(["game_id", "home_team", "away_team"])[["home_goals", "away_goals"]].sum().reset_index()

best_accuracy = 0
best_params = {}

for w_pp in [48.69, 48.7, 48.71]:
    for pim_factor in [2369.7]:
        for exp in [0.9989]:
            for w_xg in [0.1899]:
                for w_goals in [0.6789]:
                    
                    w_shots = round(1.0 - w_xg - w_goals, 2)
                    
                    if w_shots < 0:
                        continue
                        
                    features.WEIGHT_XG = w_xg
                    features.WEIGHT_GOALS = w_goals
                    features.WEIGHT_SHOTS = w_shots
                    features.EXPONENT = exp  
                    features.PIM_FACTOR = pim_factor
                    features.WEIGHT_PP = w_pp
                    
                    team_stats = features.calculate_features(df)
                    power_rankings = features.calc_win_pct(team_stats)
                    power_rankings.set_index("team", inplace=True)
                    
                    correct_predictions = 0
                    total_games = 0
                    
                    for index, row in games.iterrows():
                        if row["home_goals"] == row["away_goals"]:
                            continue 
                            
                        total_games += 1
                        actual_home_win = 1 if row["home_goals"] > row["away_goals"] else 0
                        
                        prob_home_win = predict.predict_matchup(row["home_team"], row["away_team"], power_rankings)
                        predicted_home_win = 1 if prob_home_win > 0.5 else 0
                        
                        if actual_home_win == predicted_home_win:
                            correct_predictions += 1
                            
                    accuracy = correct_predictions / total_games
                
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_params = {"xG": w_xg, "Goals": w_goals, "Shots": w_shots, "Exponent": exp, "PIM_Factor": pim_factor, "PP": w_pp}
                        print(f"New Best! Accuracy: {accuracy:.2%} | Weights -> xG: {w_xg}, Goals: {w_goals}, Shots: {w_shots} | Exp: {exp} | PIM Factor: {pim_factor} | PP: {w_pp}")

print("\n--- GRID SEARCH COMPLETE ---")
print(f"Maximum Accuracy: {best_accuracy:.2%}")
print(f"Optimal Formula: (xG * {best_params["xG"]}) + (Goals * {best_params["Goals"]}) + (Shots * {best_params["Shots"]})")
print(f"Optimal Exponent: {best_params["Exponent"]}")
print(f"Optimal PIM Factor: {best_params["PIM_Factor"]}")
print(f"Optimal PP Weight: {best_params["PP"]}")