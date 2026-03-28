-- ============================================================
-- SQL QUERIES — Subscription Churn Analysis
-- Final Year Data Science Project
-- Compatible with: SQLite, PostgreSQL, MySQL
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- 0. SETUP — Create Table (SQLite)
-- ════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS customers (
    CustomerID      TEXT PRIMARY KEY,
    Age             INTEGER,
    Gender          TEXT,
    Tenure          INTEGER,
    Contract        TEXT,
    PaymentMethod   TEXT,
    SubscriptionPlan TEXT,
    MonthlyCharges  REAL,
    TotalCharges    REAL,
    LastLoginDays   INTEGER,
    JoinMonth       TEXT,
    Churn           INTEGER,  -- 0 = Active, 1 = Churned
    ChurnLabel      TEXT
);


-- ════════════════════════════════════════════════════════════
-- 1. OVERALL KPIs
-- ════════════════════════════════════════════════════════════

-- Overall churn rate
SELECT
    COUNT(*)                                        AS total_customers,
    SUM(Churn)                                      AS total_churned,
    COUNT(*) - SUM(Churn)                           AS total_active,
    ROUND(AVG(Churn) * 100.0, 2)                   AS churn_rate_pct,
    ROUND((1 - AVG(Churn)) * 100.0, 2)             AS retention_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                   AS arpu,
    ROUND(SUM(CASE WHEN Churn=1 THEN MonthlyCharges ELSE 0 END), 2)
                                                    AS monthly_revenue_at_risk
FROM customers;


-- ════════════════════════════════════════════════════════════
-- 2. CHURN BY SEGMENT
-- ════════════════════════════════════════════════════════════

-- Churn rate by contract type
SELECT
    Contract,
    COUNT(*)                                AS total_customers,
    SUM(Churn)                              AS churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)           AS avg_monthly_charges
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;


-- Churn rate by subscription plan
SELECT
    SubscriptionPlan,
    COUNT(*)                                AS total,
    SUM(Churn)                              AS churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS churn_pct,
    ROUND(AVG(MonthlyCharges), 2)           AS arpu,
    ROUND(AVG(Tenure), 1)                  AS avg_tenure_months
FROM customers
GROUP BY SubscriptionPlan
ORDER BY churn_pct DESC;


-- Churn rate by payment method (auto-pay vs manual)
SELECT
    PaymentMethod,
    CASE
        WHEN PaymentMethod LIKE '%Auto%' THEN 'Auto-Pay'
        ELSE 'Manual Pay'
    END                                     AS PayType,
    COUNT(*)                                AS total,
    SUM(Churn)                              AS churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS churn_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_pct DESC;


-- Churn by tenure bucket
SELECT
    CASE
        WHEN Tenure BETWEEN 0  AND 3  THEN '0-3 months'
        WHEN Tenure BETWEEN 4  AND 12 THEN '3-12 months'
        WHEN Tenure BETWEEN 13 AND 24 THEN '12-24 months'
        ELSE '24+ months'
    END                                     AS tenure_bucket,
    COUNT(*)                                AS total,
    SUM(Churn)                              AS churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS churn_pct
FROM customers
GROUP BY tenure_bucket
ORDER BY churn_pct DESC;


-- Churn by age group
SELECT
    CASE
        WHEN Age BETWEEN 18 AND 25 THEN '18-25'
        WHEN Age BETWEEN 26 AND 35 THEN '26-35'
        WHEN Age BETWEEN 36 AND 45 THEN '36-45'
        WHEN Age BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END                                     AS age_group,
    COUNT(*)                                AS total,
    SUM(Churn)                              AS churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS churn_pct
FROM customers
GROUP BY age_group
ORDER BY MIN(Age);


-- ════════════════════════════════════════════════════════════
-- 3. CUSTOMER LIFETIME VALUE
-- ════════════════════════════════════════════════════════════

-- CLV by plan (simplified: ARPU × avg tenure)
SELECT
    SubscriptionPlan,
    ROUND(AVG(MonthlyCharges), 2)               AS arpu,
    ROUND(AVG(Tenure), 1)                        AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges) * AVG(Tenure), 2) AS clv_estimate
FROM customers
WHERE Churn = 0
GROUP BY SubscriptionPlan
ORDER BY clv_estimate DESC;


-- ════════════════════════════════════════════════════════════
-- 4. HIGH-RISK CUSTOMER SEGMENTS
-- ════════════════════════════════════════════════════════════

-- Top at-risk customers: month-to-month, high charges, low tenure, no auto-pay
SELECT
    CustomerID,
    Tenure,
    Contract,
    SubscriptionPlan,
    MonthlyCharges,
    PaymentMethod,
    LastLoginDays,
    'HIGH RISK' AS risk_flag
FROM customers
WHERE
    Churn = 0
    AND Contract = 'Month-to-Month'
    AND Tenure < 6
    AND MonthlyCharges > 60
    AND PaymentMethod NOT LIKE '%Auto%'
ORDER BY MonthlyCharges DESC
LIMIT 20;


-- ════════════════════════════════════════════════════════════
-- 5. REVENUE ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Monthly revenue lost to churn
SELECT
    ROUND(SUM(MonthlyCharges), 2)           AS monthly_revenue_lost,
    ROUND(SUM(MonthlyCharges) * 12, 2)     AS annual_revenue_lost,
    COUNT(*)                                AS churned_customers,
    ROUND(AVG(MonthlyCharges), 2)           AS avg_lost_per_customer
FROM customers
WHERE Churn = 1;


-- Revenue at risk by contract type
SELECT
    Contract,
    SUM(CASE WHEN Churn=1 THEN MonthlyCharges ELSE 0 END) AS revenue_lost,
    SUM(CASE WHEN Churn=0 THEN MonthlyCharges ELSE 0 END) AS revenue_retained,
    ROUND(
        SUM(CASE WHEN Churn=1 THEN MonthlyCharges ELSE 0 END) /
        SUM(MonthlyCharges) * 100, 2
    )                                                       AS pct_revenue_lost
FROM customers
GROUP BY Contract
ORDER BY revenue_lost DESC;


-- ════════════════════════════════════════════════════════════
-- 6. COHORT ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Cohort size and churn rate by join month
SELECT
    JoinMonth,
    COUNT(*)                                AS cohort_size,
    SUM(Churn)                              AS churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS churn_pct,
    ROUND(AVG(Tenure), 1)                  AS avg_tenure,
    ROUND(AVG(MonthlyCharges), 2)           AS avg_charges
FROM customers
GROUP BY JoinMonth
ORDER BY JoinMonth;


-- ════════════════════════════════════════════════════════════
-- 7. BUSINESS IMPACT SCENARIOS
-- ════════════════════════════════════════════════════════════

-- What if we reduce churn by X%?
SELECT
    'Current'       AS scenario,
    SUM(Churn)      AS churned_count,
    ROUND(SUM(CASE WHEN Churn=1 THEN MonthlyCharges ELSE 0 END)*12, 0) AS annual_rev_loss
FROM customers
UNION ALL
SELECT
    'Reduce Churn 10%',
    ROUND(SUM(Churn) * 0.90),
    ROUND(SUM(CASE WHEN Churn=1 THEN MonthlyCharges ELSE 0 END) * 12 * 0.90, 0)
FROM customers
UNION ALL
SELECT
    'Reduce Churn 25%',
    ROUND(SUM(Churn) * 0.75),
    ROUND(SUM(CASE WHEN Churn=1 THEN MonthlyCharges ELSE 0 END) * 12 * 0.75, 0)
FROM customers;
