"""
========================================================
NOTEBOOK 02 — Exploratory Data Analysis (EDA)
Subscription Churn Analysis | Final Year Project
========================================================
Run this file with: python 02_eda.py
Outputs: ../dashboard_assets/ (PNG charts)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

os.makedirs("../dashboard_assets", exist_ok=True)

# ── Style ─────────────────────────────────────────────────────
PURPLE = "#7F77DD"
TEAL   = "#1D9E75"
CORAL  = "#D85A30"
AMBER  = "#BA7517"
BLUE   = "#378ADD"
GRAY   = "#888780"
BG     = "#FAFAFA"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.family": "DejaVu Sans",
    "font.size": 11,
})

df = pd.read_csv("../data/churn_cleaned.csv")
print(f"Loaded: {df.shape}")

# ── CHART 1: Overall Churn Distribution ───────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))
vals = df["ChurnLabel"].value_counts()
bars = ax.bar(["Active", "Churned"], vals.values,
              color=[TEAL, CORAL], width=0.5, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, vals.values):
    pct = val / len(df) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 40,
            f"{val:,}\n({pct:.1f}%)", ha="center", va="bottom", fontweight="bold", fontsize=12)
ax.set_title("Overall Churn Distribution", fontsize=15, fontweight="bold", pad=15)
ax.set_ylabel("Number of Customers")
ax.set_ylim(0, vals.max() * 1.2)
plt.tight_layout()
plt.savefig("../dashboard_assets/01_churn_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 1: Churn Distribution")

# ── CHART 2: Churn by Contract Type ───────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.5))
ct = df.groupby("Contract")["Churn"].mean().sort_values(ascending=False) * 100
colors = [CORAL, AMBER, TEAL]
bars = ax.barh(ct.index, ct.values, color=colors, edgecolor="white", linewidth=1, height=0.5)
for bar, val in zip(bars, ct.values):
    ax.text(val + 0.5, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontweight="bold")
ax.set_xlabel("Churn Rate (%)")
ax.set_title("Churn Rate by Contract Type", fontsize=15, fontweight="bold", pad=15)
ax.set_xlim(0, ct.max() * 1.2)
plt.tight_layout()
plt.savefig("../dashboard_assets/02_churn_by_contract.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 2: Churn by Contract")

# ── CHART 3: Churn by Tenure Bucket ───────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.5))
order = ["0–3 months", "3–12 months", "12–24 months", "24+ months"]
tb = df.groupby("TenureBucket", observed=True)["Churn"].mean().reindex(order) * 100
bars = ax.bar(tb.index, tb.values, color=[CORAL, AMBER, BLUE, TEAL],
              edgecolor="white", linewidth=1.5, width=0.55)
for bar, val in zip(bars, tb.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", fontweight="bold")
ax.set_ylabel("Churn Rate (%)")
ax.set_title("Churn Rate by Customer Tenure", fontsize=15, fontweight="bold", pad=15)
ax.set_ylim(0, tb.max() * 1.25)
plt.tight_layout()
plt.savefig("../dashboard_assets/03_churn_by_tenure.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 3: Churn by Tenure")

# ── CHART 4: Churn by Payment Method ──────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.5))
pm = df.groupby("PaymentMethod")["Churn"].mean().sort_values(ascending=True) * 100
cmap = [TEAL if "Auto" in i else CORAL for i in pm.index]
bars = ax.barh(pm.index, pm.values, color=cmap, edgecolor="white", height=0.5)
for bar, val in zip(bars, pm.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontweight="bold")
ax.set_xlabel("Churn Rate (%)")
ax.set_title("Churn Rate by Payment Method", fontsize=15, fontweight="bold", pad=15)
ax.set_xlim(0, pm.max() * 1.2)
patches = [mpatches.Patch(color=TEAL, label="Auto-Pay"),
           mpatches.Patch(color=CORAL, label="Manual Pay")]
ax.legend(handles=patches, loc="lower right")
plt.tight_layout()
plt.savefig("../dashboard_assets/04_churn_by_payment.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 4: Churn by Payment")

# ── CHART 5: Churn by Subscription Plan ───────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))
sp = df.groupby("SubscriptionPlan")["Churn"].mean().sort_values(ascending=False) * 100
bars = ax.bar(sp.index, sp.values, color=[CORAL, AMBER, TEAL],
              width=0.45, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, sp.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
            f"{val:.1f}%", ha="center", fontweight="bold")
ax.set_ylabel("Churn Rate (%)")
ax.set_title("Churn Rate by Subscription Plan", fontsize=15, fontweight="bold", pad=15)
ax.set_ylim(0, sp.max() * 1.25)
plt.tight_layout()
plt.savefig("../dashboard_assets/05_churn_by_plan.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 5: Churn by Plan")

# ── CHART 6: Monthly Charges Distribution (Churn vs Active) ───
fig, ax = plt.subplots(figsize=(8, 4.5))
df[df["Churn"]==0]["MonthlyCharges"].plot.kde(ax=ax, color=TEAL, linewidth=2, label="Active")
df[df["Churn"]==1]["MonthlyCharges"].plot.kde(ax=ax, color=CORAL, linewidth=2, label="Churned")
ax.fill_between(ax.lines[0].get_xdata(), ax.lines[0].get_ydata(), alpha=0.15, color=TEAL)
ax.fill_between(ax.lines[1].get_xdata(), ax.lines[1].get_ydata(), alpha=0.15, color=CORAL)
ax.set_xlabel("Monthly Charges ($)")
ax.set_ylabel("Density")
ax.set_title("Monthly Charges Distribution — Churned vs Active", fontsize=14, fontweight="bold", pad=15)
ax.legend()
plt.tight_layout()
plt.savefig("../dashboard_assets/06_charges_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 6: Charges Distribution")

# ── CHART 7: Churn by Age Group ───────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4.5))
age_order = ["18–25", "26–35", "36–45", "46–60", "60+"]
ag = df.groupby("AgeGroup", observed=True)["Churn"].mean().reindex(age_order) * 100
ax.bar(ag.index, ag.values, color=PURPLE, alpha=0.85, width=0.5, edgecolor="white", linewidth=1.5)
for i, val in enumerate(ag.values):
    ax.text(i, val + 0.4, f"{val:.1f}%", ha="center", fontweight="bold")
ax.set_ylabel("Churn Rate (%)")
ax.set_title("Churn Rate by Age Group", fontsize=15, fontweight="bold", pad=15)
ax.set_ylim(0, ag.max() * 1.25)
plt.tight_layout()
plt.savefig("../dashboard_assets/07_churn_by_age.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 7: Churn by Age Group")

# ── CHART 8: Correlation Heatmap ─────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
num_cols = ["Age", "Tenure", "MonthlyCharges", "TotalCharges", "LastLoginDays", "Churn", "AutoPay"]
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, ax=ax, linewidths=0.5, cbar_kws={"shrink": 0.8})
ax.set_title("Feature Correlation with Churn", fontsize=14, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig("../dashboard_assets/08_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 8: Correlation Heatmap")

print("\n✅ All EDA charts saved to ../dashboard_assets/\n")
