"""
========================================================
NOTEBOOK 04 — Cohort Retention Analysis
Subscription Churn Analysis | Final Year Project
========================================================
Run this file with: python 04_cohort_analysis.py
Outputs: ../dashboard_assets/09_cohort_heatmap.png
         ../reports/cohort_retention.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("../dashboard_assets", exist_ok=True)
os.makedirs("../reports", exist_ok=True)

df = pd.read_csv("../data/churn_cleaned.csv")

print("=" * 60)
print("STEP 4: COHORT RETENTION ANALYSIS")
print("=" * 60)

# ── Build Cohort Table ────────────────────────────────────────
# Each cohort = users who joined in the same month
# Retention = % still active (not churned) after N months
# We simulate this using tenure as proxy for months elapsed

df["JoinMonth"] = pd.Categorical(df["JoinMonth"])
cohorts = df.groupby("JoinMonth")

# For each cohort, calculate retention at 1, 3, 6, 12, 24 months
# (users with tenure >= checkpoint who have NOT churned or whose
#  tenure is still ongoing are considered retained)
checkpoints = [1, 3, 6, 12, 24]
cohort_labels = sorted(df["JoinMonth"].unique())

retention_data = {}
for cohort, group in df.groupby("JoinMonth"):
    cohort_size = len(group)
    row = {"cohort_size": cohort_size}
    for cp in checkpoints:
        # Users who have been around for at least cp months
        reached = group[group["Tenure"] >= cp]
        # Of those, how many are active (not churned)
        retained = reached[reached["Churn"] == 0]
        # Retention rate = retained / original cohort size
        rate = len(retained) / cohort_size if cohort_size > 0 else 0
        row[f"M{cp:02d}"] = round(rate * 100, 1)
    retention_data[cohort] = row

ret_df = pd.DataFrame(retention_data).T
ret_df.index.name = "Cohort"
month_cols = [f"M{cp:02d}" for cp in checkpoints]

print("\nCohort Retention Table:")
print(ret_df[["cohort_size"] + month_cols].to_string())

# ── Plot: Cohort Retention Heatmap ───────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))

heatmap_data = ret_df[month_cols].astype(float)
# Limit to top 16 cohorts for readability
heatmap_data = heatmap_data.tail(16)

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    cmap="YlOrRd_r",
    vmin=0, vmax=100,
    ax=ax,
    linewidths=0.5,
    cbar_kws={"label": "Retention %", "shrink": 0.8},
    annot_kws={"size": 10, "weight": "bold"}
)

ax.set_title("Cohort Retention Analysis\n% of Users Still Active by Month", 
             fontsize=15, fontweight="bold", pad=20)
ax.set_xlabel("Months Since Joining", fontsize=12)
ax.set_ylabel("Join Cohort (Month)", fontsize=12)
ax.set_xticklabels([f"Month {cp}" for cp in checkpoints], fontsize=11)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)

plt.tight_layout()
plt.savefig("../dashboard_assets/09_cohort_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n✅ Cohort heatmap saved → ../dashboard_assets/09_cohort_heatmap.png")

# ── Plot: Retention Curves ────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(heatmap_data)))
for (cohort, row), color in zip(heatmap_data.iterrows(), colors):
    ax.plot(checkpoints, row.values, marker="o", linewidth=1.5,
            markersize=4, color=color, alpha=0.7)

ax.set_xlabel("Months Since Joining", fontsize=12)
ax.set_ylabel("Retention Rate (%)", fontsize=12)
ax.set_title("Retention Curves by Cohort", fontsize=14, fontweight="bold", pad=15)
ax.set_xticks(checkpoints)
ax.set_ylim(0, 100)
ax.axhline(70, linestyle="--", color="#D85A30", linewidth=1, alpha=0.7, label="70% target")
ax.legend()
ax.grid(alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("../dashboard_assets/10_retention_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Retention curves saved → ../dashboard_assets/10_retention_curves.png")

# ── Save CSV ──────────────────────────────────────────────────
ret_df.to_csv("../reports/cohort_retention.csv")
print("✅ Cohort data saved → ../reports/cohort_retention.csv")

# ── Key Insight Print ─────────────────────────────────────────
avg_m1  = heatmap_data["M01"].mean()
avg_m12 = heatmap_data["M12"].mean()
print(f"\n📊 KEY INSIGHT: Average retention at Month 1:  {avg_m1:.1f}%")
print(f"📊 KEY INSIGHT: Average retention at Month 12: {avg_m12:.1f}%")
print(f"📊 Drop-off in first year: {avg_m1 - avg_m12:.1f} percentage points")
print("\n✅ Cohort Analysis Complete!\n")
