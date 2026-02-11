# Wharton High School Data Science Competition 2026: Ice Hockey Performance Predictions
**Team: Markham Masters**

## Phase 1a: Team Performance Analysis
### 1. Overview
This project was developed for the Wharton High School Data Science competition. The data showed skewered win/loss records inconsistent with actual team performance. As such, we developed a weighted composite strength model. This model evaluates teams based on a blend of process (expected goals, shot volume), results (actual goals), and context (special teams, discipline, goaltending) in order to eliminate luck.

### 2. Strategy
Our analysis rests on the following three pillars:
1. **Process > Results**: A team's undrlying metrics are better predictors of future success than their win/loss record
2. **Context matters:** A team should account for differences in strength between the Power Play and 5v5. In addition, penalties should be penalised.
3. **Home ice advantage:** The dataset shows home teams win more than visiting teams. LLM analysis showed home teams win $~56.4\%$ of the time. Our model accounts for this bias.

### 3. Mathematical Methodology
We calculate an "Offensive Score" and "Defensive Score" for each team using a weighted formula. This approach balances the following metrics:
* **xG (Expected goals)**: Measures the quality of chances created. Weight: $40\%$.
* **Goals:** Measures the actual results. Weight: $40\%$.
* **Shots:** Measures possession and accounts for team skill. It is meant to minimise luck in our assessment. Weight: $20\%$.

The raw score is then adjusted for special cases.
We add a bonus based on xG generated per 60 minutes of power play time. We also penalise a team's defensive score based on their total penalty minutes.

To convert these scores into a single "Team Strength" metric (Win Percentage), we use the Pythagorean Expectation formula given as:
$$
\text{Win \%} = \frac{(\text{Offensive Score})^{2.15}}{(\text{Offensive Score})^{2.15} + (\text{Defensive Score})^{2.15}}
$$

The exponent of $2.15$ was selected for being optimal for hockey.

To predict the probability of a team with win percentage $A$ (home) beating a team with win percentage $B$, the Log5 formula is used plus the home ice advantage bonus:
$$
P(A\text{ Wins}) = \frac{A(1 - B)}{A(1 - B) + B(1 - A)} + 6\%
$$

### 4. Code Structure
The project is composed of three Python files.

**features.py**
This module handles data cleaning and feature analysis.
* clean_data(df): Takes in the data frame. It filters out empty net situations to prevent skewing defensive stats. This is a situation where the net is left unguarded and the goalie takes an offensive position.
* calculate_special_teams(df): Aggregates Power Play data to find xG per 60 minutes.
* calculate_discipline(df): Aggregates Penalty Minutes to measure team discipline.
* calculate_features(df): Merges 5v5 stats, special teams, and discipline into the final season_stats dataframe and calculates the composite scores.

**predict.py**
This module is used to predict win probabilities for the given matchups. 
* predict_matchup(home, away, rankings): Implementation of the Log5 formula. Returns the final probability of home team winning.

**main.py**
The execution script. It loads the raw data, calls features.py, loads the matchups and predicts the probability of home team winning each matchup.

## Phase 1b: Line Performance Analysis

## Phase 1c: Data Visualisation