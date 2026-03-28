"""
========================================================
NOTEBOOK 03 — Key Business Metrics
Subscription Churn Analysis | Final Year Project
========================================================
Run this file with: python 03_metrics.py
Outputs: console report + ../reports/metrics_summary.csv
"""

import pandas as pd
import numpy as np
import os

os.makedirs("../reports", exist_ok=True)
df = pd.read_csv("../data/churn_cleaned.csv")

print("=" * 60)
print("STEP 3: KEY BUSINESS METRICS")
print("=" * 60)

# ── 1. Overall KPIs ───────────────────────────────────────────
total_customers   = len(df)
total_churned     = df["Churn"].sum()
total_active      = total_customers - total_churned
churn_rate        = total_churned / total_customers
retention_rate    = 1 - churn_rate
total_revenue     = df["MonthlyCharges"].sum()
arpu              = total_revenue / total_customers
revenue_churned   = df[df["Churn"]==1]["MonthlyCharges"].sum()

print(f"\n{'─'*40}")
print(f"{'METRIC':<30} {'VALUE':>12}")
print(f"{'─'*40}")
print(f"{'Total Customers':<30} {total_customers:>12,}")
print(f"{'Active Customers':<30} {total_active:>12,}")
print(f"{'Churned Customers':<30} {total_churned:>12,}")
print(f"{'Churn Rate':<30} {churn_rate:>11.2%}")
print(f"{'Retention Rate':<30} {retention_rate:>11.2%}")
print(f"{'ARPU (Monthly)':<30} ${arpu:>11.2f}")
print(f"{'Monthly Revenue at Risk':<30} ${revenue_churned:>10,.2f}")
print(f"{'─'*40}")

# ── 2. Customer Lifetime Value (CLV) ─────────────────────────
avg_tenure_active = df[df["Churn"]==0]["Tenure"].mean()
clv_overall = arpu * (1 / churn_rate)  # simplified CLV
clv_by_plan = df.groupby("SubscriptionPlan").apply(
    lambda x: (x["MonthlyCharges"].mean()) * (x["Tenure"].mean())
).round(2)

print(f"\n{'─'*40}")
print(f"{'CUSTOMER LIFETIME VALUE':}")
print(f"{'─'*40}")
print(f"{'Avg Tenure (Active Users)':<30} {avg_tenure_active:.1f} months")
print(f"{'CLV (Overall Estimate)':<30} ${clv_overall:>10,.2f}")
print("\nCLV by Subscription Plan:")
for plan, val in clv_by_plan.items():
    print(f"  {plan:<28} ${val:>10,.2f}")

# ── 3. Churn Rate by Segment ──────────────────────────────────
print(f"\n{'─'*40}")
print("CHURN RATE BY SEGMENT")
print(f"{'─'*40}")

segments = {
    "Contract Type": "Contract",
    "Subscription Plan": "SubscriptionPlan",
    "Tenure Bucket": "TenureBucket",
    "Auto-Pay": "AutoPay",
}
for label, col in segments.items():
    print(f"\n{label}:")
    seg = df.groupby(col, observed=True).agg(
        Total=("Churn","count"),
        Churned=("Churn","sum"),
        ChurnRate=("Churn","mean")
    ).sort_values("ChurnRate", ascending=False)
    seg["ChurnRate"] = (seg["ChurnRate"]*100).round(1).astype(str) + "%"
    print(seg.to_string())

# ── 4. Revenue Impact ─────────────────────────────────────────
print(f"\n{'─'*40}")
print("REVENUE IMPACT ANALYSIS")
print(f"{'─'*40}")
ann_loss = revenue_churned * 12
print(f"\n  Monthly Revenue Lost:    ${revenue_churned:>10,.2f}")
print(f"  Annualized Revenue Lost: ${ann_loss:>10,.2f}")
print(f"  If churn reduced by 10%: Save ${ann_loss * 0.10:>8,.2f}/year")
print(f"  If churn reduced by 25%: Save ${ann_loss * 0.25:>8,.2f}/year")

# ── 5. Save Summary ───────────────────────────────────────────
summary = pd.DataFrame({
    "Metric": ["Total Customers","Active Customers","Churned Customers",
               "Churn Rate %","Retention Rate %","ARPU ($)","Monthly Revenue at Risk ($)",
               "Annual Revenue at Risk ($)","CLV Estimate ($)"],
    "Value": [total_customers, total_active, total_churned,
              round(churn_rate*100,2), round(retention_rate*100,2),
              round(arpu,2), round(revenue_churned,2),
              round(ann_loss,2), round(clv_overall,2)]
})
summary.to_csv("../reports/metrics_summary.csv", index=False)
print("\n[SAVE] Metrics saved → ../reports/metrics_summary.csv")
print("\n✅ Metrics Analysis Complete!\n")
