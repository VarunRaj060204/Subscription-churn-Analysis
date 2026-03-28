"""
Subscription Churn Dataset Generator
Generates a realistic Netflix/Spotify-style churn dataset
"""
import pandas as pd
import numpy as np

np.random.seed(42)
N = 7043

def generate_dataset():
    customer_ids = [f"CUST-{str(i).zfill(5)}" for i in range(1, N+1)]
    age = np.random.randint(18, 72, N)
    gender = np.random.choice(["Male", "Female"], N, p=[0.49, 0.51])
    tenure = np.random.exponential(32, N).clip(1, 72).astype(int)
    contract = np.random.choice(
        ["Month-to-Month", "One Year", "Two Year"],
        N, p=[0.55, 0.25, 0.20]
    )
    payment = np.random.choice(
        ["Electronic Check", "Mailed Check", "Bank Transfer (Auto)", "Credit Card (Auto)"],
        N, p=[0.34, 0.23, 0.22, 0.21]
    )
    plan = np.random.choice(["Basic", "Standard", "Premium"], N, p=[0.35, 0.40, 0.25])
    base_charge = {"Basic": 19.99, "Standard": 49.99, "Premium": 79.99}
    monthly_charges = np.array([base_charge[p] + np.random.uniform(-2, 15) for p in plan]).round(2)
    total_charges = (monthly_charges * tenure + np.random.uniform(-10, 10, N)).clip(0).round(2)
    last_login_days = np.random.exponential(15, N).clip(0, 90).astype(int)

    # Churn probability model
    churn_prob = np.zeros(N)
    churn_prob += np.where(contract == "Month-to-Month", 0.25, 0.0)
    churn_prob += np.where(contract == "One Year", 0.05, 0.0)
    churn_prob += np.where(contract == "Two Year", 0.02, 0.0)
    churn_prob += np.where(tenure < 3, 0.20, 0.0)
    churn_prob += np.where(tenure < 12, 0.08, 0.0)
    churn_prob += np.where(payment.isin(["Electronic Check", "Mailed Check"]) if isinstance(payment, pd.Series) else np.isin(payment, ["Electronic Check", "Mailed Check"]), 0.10, 0.0)
    churn_prob += np.where(plan == "Basic", 0.08, 0.0)
    churn_prob += np.where(monthly_charges > 70, 0.06, 0.0)
    churn_prob += np.where(last_login_days > 30, 0.12, 0.0)
    churn_prob += np.random.uniform(-0.05, 0.05, N)
    churn_prob = churn_prob.clip(0.01, 0.85)
    churn = (np.random.uniform(0, 1, N) < churn_prob).astype(int)

    join_month = pd.date_range("2022-01-01", periods=24, freq="MS")
    join_dates = np.random.choice(join_month, N)

    df = pd.DataFrame({
        "CustomerID": customer_ids,
        "Age": age,
        "Gender": gender,
        "Tenure": tenure,
        "Contract": contract,
        "PaymentMethod": payment,
        "SubscriptionPlan": plan,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "LastLoginDays": last_login_days,
        "JoinMonth": pd.to_datetime(join_dates).to_period("M").astype(str),
        "Churn": churn,
        "ChurnLabel": np.where(churn == 1, "Yes", "No")
    })

    # Inject ~50 missing values for realism
    idx = np.random.choice(df.index, 50, replace=False)
    df.loc[idx[:25], "TotalCharges"] = np.nan
    df.loc[idx[25:], "LastLoginDays"] = np.nan

    return df

if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("churn_data.csv", index=False)
    print(f"Dataset generated: {len(df)} rows, {df.columns.tolist()}")
    print(f"Churn rate: {df['Churn'].mean():.2%}")
