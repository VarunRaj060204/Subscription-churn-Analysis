"""
========================================================
NOTEBOOK 05 — Churn Prediction Model
Subscription Churn Analysis | Final Year Project
========================================================
Run this file with: python 05_model.py
Outputs: ../dashboard_assets/11_feature_importance.png
         ../dashboard_assets/12_roc_curve.png
         ../dashboard_assets/13_confusion_matrix.png
         ../reports/model_results.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, accuracy_score
)

os.makedirs("../dashboard_assets", exist_ok=True)
os.makedirs("../reports", exist_ok=True)

PURPLE = "#7F77DD"
TEAL   = "#1D9E75"
CORAL  = "#D85A30"
BG     = "#FAFAFA"

df = pd.read_csv("../data/churn_cleaned.csv")

print("=" * 60)
print("STEP 5: CHURN PREDICTION MODEL")
print("=" * 60)

# ── Feature Engineering ───────────────────────────────────────
features = [
    "Age", "Tenure", "MonthlyCharges", "TotalCharges",
    "LastLoginDays", "AutoPay"
]
cat_features = ["Contract", "SubscriptionPlan", "Gender", "PaymentMethod"]

df_model = df[features + cat_features + ["Churn"]].copy()
le = LabelEncoder()
for col in cat_features:
    df_model[col] = le.fit_transform(df_model[col].astype(str))

X = df_model.drop("Churn", axis=1)
y = df_model["Churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# ── Model 1: Logistic Regression ─────────────────────────────
lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
lr.fit(X_train, y_train)
lr_pred  = lr.predict(X_test)
lr_prob  = lr.predict_proba(X_test)[:,1]
lr_acc   = accuracy_score(y_test, lr_pred)
lr_auc   = roc_auc_score(y_test, lr_prob)
print(f"\nLogistic Regression → Accuracy: {lr_acc:.4f} | AUC-ROC: {lr_auc:.4f}")

# ── Model 2: Random Forest ────────────────────────────────────
rf = RandomForestClassifier(n_estimators=200, class_weight="balanced",
                             random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
rf_pred  = rf.predict(X_test)
rf_prob  = rf.predict_proba(X_test)[:,1]
rf_acc   = accuracy_score(y_test, rf_pred)
rf_auc   = roc_auc_score(y_test, rf_prob)
print(f"Random Forest       → Accuracy: {rf_acc:.4f} | AUC-ROC: {rf_auc:.4f}")

print("\n--- Random Forest Classification Report ---")
print(classification_report(y_test, rf_pred, target_names=["Active","Churned"]))

# ── CHART 11: Feature Importance ─────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5.5), facecolor=BG)
ax.set_facecolor(BG)
feature_names = X.columns.tolist()
importances = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=True)
colors = [PURPLE if v >= importances.quantile(0.75) else "#B4B2A9" for v in importances.values]
bars = ax.barh(importances.index, importances.values, color=colors,
               edgecolor="white", height=0.6)
for bar, val in zip(bars, importances.values):
    ax.text(val + 0.002, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=10)
ax.set_xlabel("Feature Importance Score")
ax.set_title("Top Churn Predictors — Random Forest", fontsize=14, fontweight="bold", pad=15)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", alpha=0.2)
plt.tight_layout()
plt.savefig("../dashboard_assets/11_feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 11: Feature Importance")

# ── CHART 12: ROC Curve ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5.5), facecolor=BG)
ax.set_facecolor(BG)
for model, prob, name, color in [
    (lr, lr_prob, f"Logistic Regression (AUC={lr_auc:.3f})", TEAL),
    (rf, rf_prob, f"Random Forest (AUC={rf_auc:.3f})", PURPLE)
]:
    fpr, tpr, _ = roc_curve(y_test, prob)
    ax.plot(fpr, tpr, linewidth=2.5, color=color, label=name)
ax.plot([0,1],[0,1], linestyle="--", color=CORAL, linewidth=1, label="Random Classifier")
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.set_title("ROC Curve Comparison", fontsize=14, fontweight="bold", pad=15)
ax.legend(loc="lower right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(alpha=0.2)
plt.tight_layout()
plt.savefig("../dashboard_assets/12_roc_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 12: ROC Curve")

# ── CHART 13: Confusion Matrix ────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), facecolor=BG)
for ax, pred, title in zip(axes, [lr_pred, rf_pred], 
                            ["Logistic Regression", "Random Forest"]):
    ax.set_facecolor(BG)
    cm = confusion_matrix(y_test, pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["Active","Churned"], yticklabels=["Active","Churned"],
                linewidths=0.5)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
fig.suptitle("Confusion Matrix", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("../dashboard_assets/13_confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Chart 13: Confusion Matrix")

# ── Save Results ──────────────────────────────────────────────
results = pd.DataFrame({
    "Model": ["Logistic Regression", "Random Forest"],
    "Accuracy": [round(lr_acc,4), round(rf_acc,4)],
    "AUC_ROC":  [round(lr_auc,4), round(rf_auc,4)]
})
results.to_csv("../reports/model_results.csv", index=False)
print(f"\n✅ Model results saved → ../reports/model_results.csv")
print("\n✅ Model Training Complete!\n")
