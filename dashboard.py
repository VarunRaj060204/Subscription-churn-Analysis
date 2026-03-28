"""
================================================================
SUBSCRIPTION CHURN ANALYSIS — Interactive Dashboard
================================================================
Install dependencies first:
    pip install plotly dash pandas

Then run:
    python dashboard.py

Open your browser at:
    http://127.0.0.1:8050
================================================================
"""

import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Load Data ─────────────────────────────────────────────────
df = pd.read_csv("data/churn_cleaned.csv")

# ── Color Palette ──────────────────────────────────────────────
PURPLE  = "#7F77DD"
TEAL    = "#1D9E75"
CORAL   = "#D85A30"
AMBER   = "#BA7517"
BLUE    = "#378ADD"
GRAY    = "#888780"
BG      = "#F8F8F6"
CARD_BG = "#FFFFFF"

COLORS = {
    "Churned": CORAL,
    "Active":  TEAL,
    "Month-to-Month": CORAL,
    "One Year": AMBER,
    "Two Year": TEAL,
    "Basic": CORAL,
    "Standard": AMBER,
    "Premium": TEAL,
}

# ── App Init ───────────────────────────────────────────────────
app = Dash(__name__, title="Churn Analysis Dashboard")

# ── KPI Helper ─────────────────────────────────────────────────
def kpi_card(title, value, subtitle="", color=PURPLE):
    return html.Div([
        html.P(title, style={
            "fontSize": "11px", "color": "#888", "margin": "0 0 6px",
            "textTransform": "uppercase", "letterSpacing": "0.05em", "fontWeight": "500"
        }),
        html.H2(value, style={
            "fontSize": "28px", "fontWeight": "700", "margin": "0",
            "color": color
        }),
        html.P(subtitle, style={
            "fontSize": "12px", "color": "#aaa", "margin": "4px 0 0"
        }),
    ], style={
        "background": CARD_BG, "borderRadius": "12px",
        "padding": "20px 24px", "flex": "1",
        "borderLeft": f"4px solid {color}",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"
    })

# ── Layout ─────────────────────────────────────────────────────
app.layout = html.Div(style={"background": BG, "minHeight": "100vh", "fontFamily": "Segoe UI, sans-serif"}, children=[

    # ── Header ────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.H1("🧾 Subscription Churn Analysis",
                    style={"margin": "0", "fontSize": "24px", "fontWeight": "700", "color": "#1a1a1a"}),
            html.P("Netflix/Spotify-style · Made by Varun Raj",
                   style={"margin": "4px 0 0", "color": "#888", "fontSize": "13px"}),
        ]),
        html.Div([
            html.Span("● LIVE", style={"color": TEAL, "fontSize": "12px", "fontWeight": "600"}),
            html.Span(f"  {len(df):,} customers", style={"color": "#888", "fontSize": "12px", "marginLeft": "8px"}),
        ])
    ], style={
        "background": CARD_BG, "padding": "20px 32px",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "borderBottom": "1px solid #eee", "boxShadow": "0 1px 4px rgba(0,0,0,0.05)"
    }),

    # ── Filters ───────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Label("Contract Type", style={"fontSize": "12px", "color": "#888", "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filter-contract",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": c, "value": c} for c in df["Contract"].unique()],
                value="All", clearable=False,
                style={"fontSize": "13px", "minWidth": "180px"}
            ),
        ]),
        html.Div([
            html.Label("Subscription Plan", style={"fontSize": "12px", "color": "#888", "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filter-plan",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": p, "value": p} for p in df["SubscriptionPlan"].unique()],
                value="All", clearable=False,
                style={"fontSize": "13px", "minWidth": "160px"}
            ),
        ]),
        html.Div([
            html.Label("Gender", style={"fontSize": "12px", "color": "#888", "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filter-gender",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": g, "value": g} for g in df["Gender"].unique()],
                value="All", clearable=False,
                style={"fontSize": "13px", "minWidth": "130px"}
            ),
        ]),
        html.Div([
            html.Label("Payment Method", style={"fontSize": "12px", "color": "#888", "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filter-payment",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": p, "value": p} for p in df["PaymentMethod"].unique()],
                value="All", clearable=False,
                style={"fontSize": "13px", "minWidth": "210px"}
            ),
        ]),
    ], style={
        "background": CARD_BG, "padding": "16px 32px",
        "display": "flex", "gap": "24px", "alignItems": "flex-end",
        "borderBottom": "1px solid #eee", "flexWrap": "wrap"
    }),

    # ── Main Content ──────────────────────────────────────────
    html.Div(style={"padding": "24px 32px"}, children=[

        # ── KPI Row ───────────────────────────────────────────
        html.Div(id="kpi-row", style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"}),

        # ── Row 1: Churn Distribution + By Contract ───────────
        html.Div([
            html.Div([
                html.H3("Churn Overview", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-donut", style={"height": "280px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "1", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),

            html.Div([
                html.H3("Churn by Contract Type", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-contract", style={"height": "280px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "2", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "flexWrap": "wrap"}),

        # ── Row 2: Tenure + Payment ───────────────────────────
        html.Div([
            html.Div([
                html.H3("Churn by Tenure", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-tenure", style={"height": "260px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "1", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),

            html.Div([
                html.H3("Churn by Payment Method", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-payment", style={"height": "260px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "1", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "flexWrap": "wrap"}),

        # ── Row 3: Monthly Charges + Subscription Plan ────────
        html.Div([
            html.Div([
                html.H3("Monthly Charges — Active vs Churned", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-charges", style={"height": "260px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "2", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),

            html.Div([
                html.H3("Churn by Plan", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-plan", style={"height": "260px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "1", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "flexWrap": "wrap"}),

        # ── Row 4: Cohort Heatmap ─────────────────────────────
        html.Div([
            html.H3("Cohort Retention Heatmap", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 4px", "color": "#333"}),
            html.P("% of users still active by months since joining", style={"fontSize": "12px", "color": "#aaa", "margin": "0 0 12px"}),
            dcc.Graph(id="chart-cohort", style={"height": "380px"}, config={"displayModeBar": False}),
        ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                  "marginBottom": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),

        # ── Row 5: Scatter + Age ──────────────────────────────
        html.Div([
            html.Div([
                html.H3("Tenure vs Monthly Charges", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-scatter", style={"height": "300px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "2", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),

            html.Div([
                html.H3("Churn by Age Group", style={"fontSize": "14px", "fontWeight": "600", "margin": "0 0 12px", "color": "#333"}),
                dcc.Graph(id="chart-age", style={"height": "300px"}, config={"displayModeBar": False}),
            ], style={"background": CARD_BG, "borderRadius": "12px", "padding": "20px",
                      "flex": "1", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "flexWrap": "wrap"}),

        # ── Footer ────────────────────────────────────────────
        html.Div([
            html.P("🧾 Subscription Churn Analysis · Made by - Varun Raj · Built with Python & Plotly Dash",
                   style={"textAlign": "center", "color": "#bbb", "fontSize": "12px", "margin": "0"})
        ], style={"padding": "16px 0 8px"}),

    ]),
])

# ── Callback: All Charts ───────────────────────────────────────
@app.callback(
    Output("kpi-row",       "children"),
    Output("chart-donut",   "figure"),
    Output("chart-contract","figure"),
    Output("chart-tenure",  "figure"),
    Output("chart-payment", "figure"),
    Output("chart-charges", "figure"),
    Output("chart-plan",    "figure"),
    Output("chart-cohort",  "figure"),
    Output("chart-scatter", "figure"),
    Output("chart-age",     "figure"),
    Input("filter-contract","value"),
    Input("filter-plan",    "value"),
    Input("filter-gender",  "value"),
    Input("filter-payment", "value"),
)
def update_all(contract, plan, gender, payment):
    # ── Filter ────────────────────────────────────────────────
    d = df.copy()
    if contract != "All": d = d[d["Contract"] == contract]
    if plan     != "All": d = d[d["SubscriptionPlan"] == plan]
    if gender   != "All": d = d[d["Gender"] == gender]
    if payment  != "All": d = d[d["PaymentMethod"] == payment]

    total      = len(d)
    churned    = d["Churn"].sum()
    active     = total - churned
    churn_rate = churned / total if total else 0
    arpu       = d["MonthlyCharges"].mean()
    rev_risk   = d[d["Churn"]==1]["MonthlyCharges"].sum()

    layout_base = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Segoe UI, sans-serif", size=12, color="#444"),
    )

    # ── KPIs ──────────────────────────────────────────────────
    kpis = html.Div([
        kpi_card("Total Customers",        f"{total:,}",             "in filtered view",    BLUE),
        kpi_card("Churned Customers",      f"{churned:,}",           f"{churn_rate:.1%} churn rate", CORAL),
        kpi_card("Active Customers",       f"{active:,}",            f"{1-churn_rate:.1%} retention", TEAL),
        kpi_card("ARPU (Monthly)",         f"${arpu:,.2f}",          "avg revenue per user", PURPLE),
        kpi_card("Revenue at Risk/mo",     f"${rev_risk:,.0f}",      f"${rev_risk*12:,.0f} annualized", AMBER),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "width": "100%"})

    # ── Donut ─────────────────────────────────────────────────
    fig_donut = go.Figure(go.Pie(
        labels=["Active", "Churned"], values=[active, churned],
        hole=0.62, marker_colors=[TEAL, CORAL],
        textinfo="label+percent", textfont_size=13,
        hovertemplate="%{label}: %{value:,}<extra></extra>"
    ))
    fig_donut.add_annotation(text=f"<b>{churn_rate:.1%}</b><br><span style='font-size:10px'>churn</span>",
                              x=0.5, y=0.5, showarrow=False, font_size=18, align="center")
    fig_donut.update_layout(**layout_base, showlegend=False)

    # ── Contract Bar ──────────────────────────────────────────
    ct = d.groupby("Contract")["Churn"].mean().reset_index()
    ct.columns = ["Contract", "ChurnRate"]
    ct["ChurnRate"] *= 100
    ct = ct.sort_values("ChurnRate", ascending=True)
    fig_contract = px.bar(ct, x="ChurnRate", y="Contract", orientation="h",
                          color="Contract",
                          color_discrete_map={"Month-to-Month": CORAL, "One Year": AMBER, "Two Year": TEAL},
                          text=ct["ChurnRate"].apply(lambda x: f"{x:.1f}%"))
    fig_contract.update_traces(textposition="outside", marker_line_width=0)
    fig_contract.update_layout(**layout_base, showlegend=False,
                                xaxis=dict(title="Churn Rate (%)", gridcolor="#f0f0f0"),
                                yaxis=dict(title=""))

    # ── Tenure Bar ────────────────────────────────────────────
    order = ["0–3 months", "3–12 months", "12–24 months", "24+ months"]
    tb = d.groupby("TenureBucket", observed=True)["Churn"].mean().reindex(order).reset_index()
    tb.columns = ["Bucket", "ChurnRate"]
    tb["ChurnRate"] *= 100
    fig_tenure = px.bar(tb, x="Bucket", y="ChurnRate",
                        color="ChurnRate", color_continuous_scale=["#1D9E75","#BA7517","#D85A30"],
                        text=tb["ChurnRate"].apply(lambda x: f"{x:.1f}%"))
    fig_tenure.update_traces(textposition="outside", marker_line_width=0)
    fig_tenure.update_layout(**layout_base, showlegend=False, coloraxis_showscale=False,
                              xaxis=dict(title=""), yaxis=dict(title="Churn Rate (%)", gridcolor="#f0f0f0"),
                              bargap=0.35)

    # ── Payment Bar ───────────────────────────────────────────
    pm = d.groupby("PaymentMethod")["Churn"].mean().reset_index()
    pm.columns = ["Payment", "ChurnRate"]
    pm["ChurnRate"] *= 100
    pm = pm.sort_values("ChurnRate", ascending=True)
    pm["Color"] = pm["Payment"].apply(lambda x: TEAL if "Auto" in x else CORAL)
    fig_payment = px.bar(pm, x="ChurnRate", y="Payment", orientation="h",
                         color="Color", color_discrete_map={TEAL: TEAL, CORAL: CORAL},
                         text=pm["ChurnRate"].apply(lambda x: f"{x:.1f}%"))
    fig_payment.update_traces(textposition="outside", marker_line_width=0)
    fig_payment.update_layout(**layout_base, showlegend=False,
                               xaxis=dict(title="Churn Rate (%)", gridcolor="#f0f0f0"),
                               yaxis=dict(title=""))

    # ── Charges Box ───────────────────────────────────────────
    fig_charges = go.Figure()
    fig_charges.add_trace(go.Violin(
        x=d[d["Churn"]==0]["MonthlyCharges"], name="Active",
        side="negative", line_color=TEAL, fillcolor=TEAL, opacity=0.6,
        meanline_visible=True
    ))
    fig_charges.add_trace(go.Violin(
        x=d[d["Churn"]==1]["MonthlyCharges"], name="Churned",
        side="positive", line_color=CORAL, fillcolor=CORAL, opacity=0.6,
        meanline_visible=True
    ))
    fig_charges.update_layout(**layout_base, showlegend=True,
                               legend=dict(orientation="h", y=1.1),
                               xaxis=dict(title="Monthly Charges ($)", gridcolor="#f0f0f0"),
                               yaxis=dict(visible=False),
                               violingap=0)

    # ── Plan Bar ──────────────────────────────────────────────
    sp = d.groupby("SubscriptionPlan")["Churn"].mean().reset_index()
    sp.columns = ["Plan", "ChurnRate"]
    sp["ChurnRate"] *= 100
    sp = sp.sort_values("ChurnRate", ascending=False)
    fig_plan = px.bar(sp, x="Plan", y="ChurnRate",
                      color="Plan",
                      color_discrete_map={"Basic": CORAL, "Standard": AMBER, "Premium": TEAL},
                      text=sp["ChurnRate"].apply(lambda x: f"{x:.1f}%"))
    fig_plan.update_traces(textposition="outside", marker_line_width=0)
    fig_plan.update_layout(**layout_base, showlegend=False,
                            xaxis=dict(title=""), yaxis=dict(title="Churn Rate (%)", gridcolor="#f0f0f0"),
                            bargap=0.4)

    # ── Cohort Heatmap ────────────────────────────────────────
    checkpoints = [1, 3, 6, 12, 24]
    cohort_rows = {}
    for cohort, group in df.groupby("JoinMonth"):
        sz = len(group)
        row = {}
        for cp in checkpoints:
            reached  = group[group["Tenure"] >= cp]
            retained = reached[reached["Churn"] == 0]
            row[f"M{cp:02d}"] = round(len(retained) / sz * 100, 1) if sz else 0
        cohort_rows[cohort] = row
    cohort_df = pd.DataFrame(cohort_rows).T
    month_cols = [f"M{cp:02d}" for cp in checkpoints]
    z_vals  = cohort_df[month_cols].astype(float).values.tolist()
    y_labels = cohort_df.index.tolist()
    x_labels = [f"Month {cp}" for cp in checkpoints]
    fig_cohort = go.Figure(go.Heatmap(
        z=z_vals, x=x_labels, y=y_labels,
        colorscale=[[0,"#D85A30"],[0.5,"#BA7517"],[1,"#1D9E75"]],
        zmin=0, zmax=100,
        text=[[f"{v:.0f}%" for v in row] for row in z_vals],
        texttemplate="%{text}", textfont={"size": 11},
        hovertemplate="Cohort: %{y}<br>%{x}: %{z:.1f}%<extra></extra>",
        colorbar=dict(title="Retention %", thickness=14, len=0.8)
    ))
    fig_cohort.update_layout(**layout_base,
                              xaxis=dict(side="top"),
                              yaxis=dict(autorange="reversed"))

    # ── Scatter ───────────────────────────────────────────────
    sample = d.sample(min(1500, len(d)), random_state=42)
    fig_scatter = px.scatter(
        sample, x="Tenure", y="MonthlyCharges",
        color="ChurnLabel",
        color_discrete_map={"Yes": CORAL, "No": TEAL},
        opacity=0.55, size_max=6,
        hover_data=["SubscriptionPlan", "Contract"],
        labels={"ChurnLabel": "Status", "Tenure": "Tenure (months)", "MonthlyCharges": "Monthly Charges ($)"}
    )
    fig_scatter.update_traces(marker=dict(size=5))
    fig_scatter.update_layout(**layout_base,
                               legend=dict(title="", orientation="h", y=1.1),
                               xaxis=dict(gridcolor="#f0f0f0"),
                               yaxis=dict(gridcolor="#f0f0f0"))

    # ── Age Bar ───────────────────────────────────────────────
    age_order = ["18–25", "26–35", "36–45", "46–60", "60+"]
    ag = d.groupby("AgeGroup", observed=True)["Churn"].mean().reindex(age_order).reset_index()
    ag.columns = ["Age", "ChurnRate"]
    ag["ChurnRate"] *= 100
    fig_age = px.bar(ag, x="Age", y="ChurnRate",
                     color="ChurnRate", color_continuous_scale=["#1D9E75","#BA7517","#D85A30"],
                     text=ag["ChurnRate"].apply(lambda x: f"{x:.1f}%"))
    fig_age.update_traces(textposition="outside", marker_line_width=0)
    fig_age.update_layout(**layout_base, showlegend=False, coloraxis_showscale=False,
                           xaxis=dict(title=""), yaxis=dict(title="Churn Rate (%)", gridcolor="#f0f0f0"),
                           bargap=0.35)

    return kpis, fig_donut, fig_contract, fig_tenure, fig_payment, fig_charges, fig_plan, fig_cohort, fig_scatter, fig_age


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("🧾  Churn Analysis Dashboard starting...")
    print("="*55)
    print("  Open your browser and go to:")
    print("  👉  http://127.0.0.1:8050")
    print("  Press Ctrl+C to stop the server")
    print("="*55 + "\n")
    app.run(debug=False)
