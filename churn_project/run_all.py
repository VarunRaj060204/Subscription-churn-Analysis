"""
run_all.py — Execute the entire Subscription Churn Analysis pipeline
Run from project root: python run_all.py
"""
import subprocess, sys, os, time

steps = [
    ("Generate Dataset",        "data/generate_data.py",         "data"),
    ("Data Cleaning",           "notebooks/01_data_cleaning.py", "notebooks"),
    ("Exploratory Data Analysis","notebooks/02_eda.py",           "notebooks"),
    ("Key Metrics",             "notebooks/03_metrics.py",        "notebooks"),
    ("Cohort Analysis",         "notebooks/04_cohort_analysis.py","notebooks"),
    ("Churn Prediction Model",  "notebooks/05_model.py",          "notebooks"),
]

print("=" * 65)
print("🧾 SUBSCRIPTION CHURN ANALYSIS — FULL PIPELINE RUN")
print("=" * 65)

total_start = time.time()
for i, (name, script, cwd) in enumerate(steps, 1):
    print(f"\n[{i}/{len(steps)}] Running: {name}")
    print("─" * 45)
    start = time.time()
    result = subprocess.run(
        [sys.executable, os.path.basename(script)],
        cwd=os.path.join(os.path.dirname(__file__), cwd),
        capture_output=False
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"    ✅ Done in {elapsed:.1f}s")
    else:
        print(f"    ❌ Failed! Check error above.")
        sys.exit(1)

total = time.time() - total_start
print("\n" + "=" * 65)
print(f"✅ ALL STEPS COMPLETE in {total:.1f}s")
print("\nOutputs:")
print("  📁 data/churn_cleaned.csv          — Cleaned dataset")
print("  📁 dashboard_assets/*.png          — 13 analysis charts")
print("  📁 reports/metrics_summary.csv     — KPI summary")
print("  📁 reports/cohort_retention.csv    — Cohort table")
print("  📁 reports/model_results.csv       — ML model scores")
print("=" * 65)
