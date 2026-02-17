import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np 

def create_visualisation(power_rankings, disparity_df):
    merged_df = power_rankings[["win_pct"]].join(disparity_df[["Disparity_Ratio"]], how="inner")
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 8))
    
    ax = plt.gca()

    scatter = sns.scatterplot(
        data=merged_df, 
        x="Disparity_Ratio", 
        y="win_pct", 
        s=100,             
        color="#1f77b4",   
        alpha=0.6
    )
    
    sns.regplot(
        data=merged_df, 
        x="Disparity_Ratio", 
        y="win_pct", 
        scatter=False, 
        color="#d62728", 
        line_kws={"label": "Trend Line"}
    )

    x = merged_df["Disparity_Ratio"]
    y = merged_df["win_pct"]
    
    m, c = np.polyfit(x, y, 1)
    
    correlation = np.corrcoef(x, y)[0, 1]
    r_squared = correlation**2
    
    equation_text = f"y = {m:.3f}x + {c:.3f}\n$R^2$ = {r_squared:.3f}"
    
    plt.text(0.95, 0.95, equation_text, transform=ax.transAxes,
             fontsize=12, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9, edgecolor="gray"))
    
    plt.title("Impact of Offensive Line Disparity on Team Success", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Offensive Line Disparity Ratio (Line 1 xG / Line 2 xG)", fontsize=12, labelpad=10)
    plt.ylabel("Predicted Win Percentage (Team Strength)", fontsize=12, labelpad=10)
    
    plt.text(0.02, 0.02, "← More Balanced Lines", transform=ax.transAxes, 
             color="green", fontsize=11, fontweight='bold', ha='left', va='bottom',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
             
    plt.text(0.98, 0.02, "Top-Heavy Lines →", transform=ax.transAxes, 
             color="orange", fontsize=11, fontweight='bold', ha='right', va='bottom',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    merged_df = merged_df.sort_values("win_pct", ascending=False)
    
    for team in merged_df.head(3).index:
        x_pos = merged_df.loc[team, "Disparity_Ratio"]
        y_pos = merged_df.loc[team, "win_pct"]
        
        plt.text(x_pos + 0.01, y_pos, team, 
                 fontsize=10, color="green", weight='bold', va='center')

    for team in merged_df.tail(3).index:
        x_pos = merged_df.loc[team, "Disparity_Ratio"]
        y_pos = merged_df.loc[team, "win_pct"]
        
        plt.text(x_pos + 0.01, y_pos, team, 
                 fontsize=10, color="#d62728", weight='bold', va='center')

    plt.tight_layout()
    
    plt.savefig("phase1c_disparity_vs_success.png", dpi=300)
    print("Visualisation saved as 'phase1c_disparity_vs_success.png'")
    plt.show()