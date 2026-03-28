"""
========================================================
NOTEBOOK 01 — Data Cleaning
Subscription Churn Analysis | Final Year Project
========================================================
Run this file with: python 01_data_cleaning.py
Outputs: ../data/churn_cleaned.csv
"""

import pandas as pd
import numpy as np
import os

print("=" * 60)
print("STEP 1: DATA CLEANING")
print("=" * 60)

# ── 1. Load Raw Data ─────────────────────────────────────────
df = pd.read_csv("../data/churn_data.csv")
print(f"\n[LOAD] Raw dataset: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"[LOAD] Columns: {df.columns.tolist()}")

# ── 2. Initial Inspection ─────────────────────────────────────
print("\n--- Missing Values ---")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\n--- Data Types ---")
print(df.dtypes)

print("\n--- Duplicates ---")
dupes = df.duplicated(subset="CustomerID").sum()
print(f"Duplicate CustomerIDs: {dupes}")

# ── 3. Handle Missing Values ──────────────────────────────────
# TotalCharges: fill with Tenure × MonthlyCharges estimate
df["TotalCharges"] = df["TotalCharges"].fillna(
    df["Tenure"] * df["MonthlyCharges"]
).round(2)

# LastLoginDays: fill with median per plan
df["LastLoginDays"] = df.groupby("SubscriptionPlan")["LastLoginDays"].transform(
    lambda x: x.fillna(x.median())
).round(0).astype(int)

print(f"\n[CLEAN] Missing values after fix: {df.isnull().sum().sum()}")

# ── 4. Remove Duplicates ──────────────────────────────────────
df = df.drop_duplicates(subset="CustomerID")
print(f"[CLEAN] Rows after deduplication: {len(df)}")

# ── 5. Convert & Encode Columns ──────────────────────────────
# Churn is already 0/1 — keep both ChurnLabel and Churn
# Add tenure buckets
df["TenureBucket"] = pd.cut(
    df["Tenure"],
    bins=[0, 3, 12, 24, 72],
    labels=["0–3 months", "3–12 months", "12–24 months", "24+ months"]
)

# Age groups
df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[17, 25, 35, 45, 60, 100],
    labels=["18–25", "26–35", "36–45", "46–60", "60+"]
)

# Charge bracket
df["ChargeBracket"] = pd.cut(
    df["MonthlyCharges"],
    bins=[0, 30, 55, 75, 200],
    labels=["Low (<$30)", "Mid ($30–55)", "High ($55–75)", "Very High (>$75)"]
)

# Payment type simplified
df["AutoPay"] = df["PaymentMethod"].isin(
    ["Bank Transfer (Auto)", "Credit Card (Auto)"]
).astype(int)

print("\n--- Cleaned Dataset Overview ---")
print(df[["CustomerID","Tenure","TenureBucket","AgeGroup","AutoPay","Churn"]].head(5).to_string())

# ── 6. Save ───────────────────────────────────────────────────
df.to_csv("../data/churn_cleaned.csv", index=False)
print(f"\n[SAVE] Cleaned data saved → ../data/churn_cleaned.csv")
print(f"[SAVE] Final shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"[SAVE] Churn rate: {df['Churn'].mean():.2%}")
print("\n✅ Data Cleaning Complete!\n")
