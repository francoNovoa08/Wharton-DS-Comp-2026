# Wharton High School Data Science Competition 2026: Ice Hockey Performance Predictions
**Team: Markham Masters**

## Phase 1a: Team Performance Analysis
### 1. Overview
This project was developed for the Wharton High School Data Science competition. The data showed skewered win/loss records inconsistent with actual team performance. As such, we developed a weighted composite strength model. This model evaluates teams based on a blend of process (expected goals, shot volume), results (actual goals), and context (special teams, discipline, goaltending) in order to eliminate luck.

### 2. Strategy
Our analysis rests on the following three pillars:
1. **All metrics should be considered**: Statistics should be analyses instead of arbitrarily being chosen as better.
2. **Context matters:** A team should account for differences in strength between the Power Play and 5v5. In addition, penalties should be penalised.
3. **Home ice advantage:** The dataset shows home teams win more than visiting teams. LLM analysis showed home teams win $\approx 56.4\%$ of the time. Our model accounts for this bias.

### 3. Mathematical Methodology
We calculate an "Offensive Score" and "Defensive Score" for each team using a weighted formula. This approach balances the following metrics:
* **xG (Expected goals)**: Measures the quality of chances created. 
* **Goals:** Measures the actual results. 
* **Shots:** Measures possession and accounts for team skill. It is meant to minimise luck in our assessment. 

The raw score is then adjusted for special cases.
We add a bonus based on xG generated per 60 minutes of power play time. This is added as a bonus to the offensive score. 

The offensive and defensive scores are divided by the total time on ice to create a per-hour rate.

We also penalise a team's defensive score based on their total penalty minutes. Team with high penalty minutes have their defensive score worsened by a factor proportional to their indiscipline. The power play bonus and penalties are proportional multipliers.

The factors and weights were chosen by continously backtesting to find optimal values for the highest accuracy. The raw totals are not weighted together. Rather, a min-max normalisation is performed on expected goals, actual goals, and shots, before any weights are applied. They are normalised for a scale from $0$ to $1$. These are applied evenly so a greater volume of a given statistic does not skewer results.

To convert these scores into a single "Team Strength" metric (Win Percentage), we used the Pythagorean Expectation formula given as:

$$
\text{Win \%} = \frac{(\text{Offensive Score})^{EXPONENT}}{(\text{Offensive Score})^{EXPONENT} + (\text{Defensive Score})^{EXPONENT}}
$$

The EXPONENT variable value was chosen through optimising several parameter weights and backtesting.

To predict the probability of a team with win percentage $A$ (home) beating a team with win percentage $B$, the Log5 formula is used plus the home ice advantage bonus:

$$
P(A\text{ Wins}) = \frac{A(1 - B)}{A(1 - B) + B(1 - A)} 
$$¿

LLM analysis suggests home teams win around $6\%$ more than away teams. This implies an even match with a $0.50$ win probability for the home team should become a $0.56$ win probability for the home team and a $0.44$ win probability for the away team. However, adding a flat percentage is not always accurate and may cause win probabilities to exceed $1.0$. As such, an odds ratio is used.

The odds $O$ are given by the probability of an event $P$ as follows:

$$
O = \frac{P}{1-P}
$$

For the even game, $O_e$ is:

$$
O_e = \frac{0.50}{1-0.50} = 1.0
$$

The target odds $O_t$ where $P=0.56$ is given by:

$$
O_t = \frac{0.56}{1-0.56}\approx 1.27
$$

A multiplier that converts some neutral odds into the target odds is given by:

$$
\frac{1.27}{1.0} = 1.27
$$

Hence for every probability of a team winning, the probability is converted into odds. The odds are multiplied by this multiplier $(1.27)$ to give the home team advantage and then converted back into a probability.

## Phase 1b: Line Performance Analysis
### 1. Overview
The second phase of our analysis measures offensive line quality disparity. The goal is to quantify how much quality decreases between a team's 1st line and 2nd line.

### 2. Methodology
We accounted for the following two variables:
1. **Time on Ice:** Lines play different minutes per game.
2. **Quality of Competition:** First lines typically face stronger opponents than second lines. A lower performance should not be penalised because of this.

To account for time on ice, all metrics were normalised to a "Per 60 minutes" rate. 

We calculate a "Defensive Strength Rating" for every defensive pairing in the league. This is defined as the xG Allowed per 60 Minutes by that specific pair. Hence, a lower score indicates a better defense.

We calculate the Average Defensive Strength Faced for every offensive line. We then calculate an adjusted xG by comparing the specific defense faced to the global average. 

If a line scores heavily against a weak defense, the xG is multiplied by a ratio $<1$, and their score is penalised.
Conversely, an offense against a strong defense multiplies the xG by a ratio $>1$ and their score is boosted.

Finally, we calculate the Disparity Ratio for each team. This is defined as the Adjusted Performance of the 1st Line divided by the Adjusted Performance of the 2nd Line.

## Phase 1c: Data Visualisation
For Phase 1c, we produced a chart of the predicted win percentage (team strength) derived in Phase 1a (y-axis) against the offensive line disparity ratio derived in Phase 1b (x-axis). This chart should show the correlation between team strength and line disparity. 

A positive correlation would imply less balanced lines correlate with greater team strengths, suggesting a stellar first line is more important for winning than having balanced lines. Conversely, a negative correlation would imply balancing was correlated with a greater team strength.

We added a red area representing the $95\%$ confidence interval. This area represents the margin of error of the trendline. 

The produced graph showed a generally weak negative correlation between team strength and offensive line disparity. While stronger teams were more likely to have balanced offensive lines, this was not deterministic of their strength. The very low $R^2$ value suggests a very poor fit of the linear model.

## Backtesting
The weights for goals, expected goals, shots, the exponent for the Log5 formula, and the penalty minutes factor were defined through continous backtesting. After creating the model, it was tested against the original games. Several weights and exponents were chosen to find the ideal values that produced the highest accuracy.

The "continous backtesting" involved a grid search algorithm, whereby many permutations of factors were tested to find the ones that gave the highest accuracy against the initial dataset. This was performed on the variables of goals, expected goals, Log5 exponent, penalty minutes, and power play weight.