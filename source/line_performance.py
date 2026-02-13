import pandas as pd
import numpy as np
from features import clean_data

class LinePerformanceAnalyser:

    def __init__(self, path):
        self.raw_df = pd.read_csv(path)
        self.df = clean_data(self.raw_df)
        self.def_map = {}
        self.global_def_avg = 0

    def _calculate_rates(self):
        self.df = self.df[
            (self.df["home_def_pairing"] != "empty_net_line") & 
            (self.df["away_def_pairing"] != "empty_net_line")
        ].copy()

        home_plays = self.df[["home_team", "home_off_line", "away_team", "away_def_pairing", "home_xg", "toi"]].copy()
        home_plays.columns = ["off_team", "off_line", "def_team", "def_pair", "xg", "toi"]

        away_plays = self.df[["away_team", "away_off_line", "home_team", "home_def_pairing", "away_xg", "toi"]].copy()
        away_plays.columns = ["off_team", "off_line", "def_team", "def_pair", "xg", "toi"]

        self.shifts = pd.concat([home_plays, away_plays])
        self.shifts = self.shifts[self.shifts["toi"] > 0].copy()

    def _calculate_defensive_strength(self):
        def_stats = self.shifts.groupby(["def_team", "def_pair"])[["xg", "toi"]].sum().reset_index()

        def_stats["def_strength_rating"] = (def_stats["xg"] / def_stats["toi"]) * 3600

        def_stats["id"] = def_stats["def_team"] + "_" + def_stats["def_pair"].astype(str)
        self.def_map = def_stats.set_index("id")["def_strength_rating"].to_dict()
        self.global_def_avg = (def_stats["xg"].sum() / def_stats["toi"].sum()) * 3600

    def _get_opponent_strength(self, row):
        """
        Helper to look up the strength of the specific defensive pair faced.
        """
        opponent_id = f"{row["def_team"]}_{row["def_pair"]}"
        return self.def_map.get(opponent_id, self.global_def_avg)
    
    def analyse(self):
        self._calculate_rates()
        self._calculate_defensive_strength()

        self.shifts["opp_def_rating"] = self.shifts.apply(self._get_opponent_strength, axis=1)
        
        self.shifts["weighted_opp_def"] = self.shifts["opp_def_rating"] * self.shifts["toi"]

        line_stats = self.shifts.groupby(["off_team", "off_line"]).agg({
            "xg": "sum",
            "toi": "sum",
            "weighted_opp_def": "sum"
        }).reset_index()

        line_stats["observed_xg_60"] = (line_stats["xg"] / line_stats["toi"]) * 3600

        line_stats["avg_def_faced"] = line_stats["weighted_opp_def"] / line_stats["toi"]
        line_stats["adj_xg_60"] = line_stats["observed_xg_60"] * (self.global_def_avg / line_stats["avg_def_faced"])

        return line_stats
    
    def get_disparity(self, line_stats):
        """
        Calculates the disparity ratio between 1st and 2nd lines using the ADJUSTED metric.
        """
        valid_lines = ["first_off", "second_off"]
        df_filtered = line_stats[line_stats["off_line"].isin(valid_lines)].copy()

        pivot = df_filtered.pivot(index="off_team", columns="off_line", values="adj_xg_60")
        
        pivot.rename(columns={"first_off": "Line_1_Adj", "second_off": "Line_2_Adj"}, inplace=True)

        pivot["Disparity_Ratio"] = pivot["Line_1_Adj"] / pivot["Line_2_Adj"]

        return pivot.sort_values("Disparity_Ratio", ascending=False)