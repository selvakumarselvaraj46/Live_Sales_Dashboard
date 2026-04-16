import random
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Enterprise Revenue Control Room",
    layout="wide",
    page_icon="📊"
)

# -----------------------------
# PREMIUM DARK THEME – Power BI Style
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-base:      #0b0f1a;
    --bg-panel:     #111827;
    --bg-card:      #1a2236;
    --border:       #1f2d45;
    --accent-blue:  #3b82f6;
    --accent-cyan:  #06b6d4;
    --accent-green: #10b981;
    --accent-amber: #f59e0b;
    --accent-rose:  #f43f5e;
    --accent-purple:#8b5cf6;
    --text-primary: #e2e8f0;
    --text-muted:   #64748b;
    --text-label:   #94a3b8;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 10%, #0d1b2e 0%, #0b0f1a 55%, #050810 100%);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
    background: #080d16;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-label) !important; }
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: var(--accent-blue) !important;
}

h1 {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em;
    background: linear-gradient(90deg, #60a5fa, #22d3ee, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem !important;
}
h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.04em;
    font-weight: 600 !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(145deg, #1a2236 0%, #131c30 100%);
    padding: 22px 18px 18px;
    border-radius: 12px;
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(59,130,246,0.18);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-blue::before   { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.kpi-green::before  { background: linear-gradient(90deg, #10b981, #34d399); }
.kpi-amber::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-purple::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

.kpi-icon  { font-size: 22px; margin-bottom: 8px; display: block; }
.kpi-title {
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 30px; font-weight: 700;
    line-height: 1; margin-bottom: 6px;
}
.kpi-blue   .kpi-value { color: #60a5fa; }
.kpi-green  .kpi-value { color: #34d399; }
.kpi-amber  .kpi-value { color: #fbbf24; }
.kpi-purple .kpi-value { color: #a78bfa; }
.kpi-sub { font-size: 11px; color: var(--text-muted); letter-spacing: 0.04em; }

.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 24px 0;
}

/* ── Pulse dot ── */
.pulse-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #10b981;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
    vertical-align: middle;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
    70%  { box-shadow: 0 0 0 8px rgba(16,185,129,0); }
    100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid var(--border) !important;
    overflow: hidden;
}

.footer {
    text-align: center;
    padding: 16px 0 8px;
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    border-top: 1px solid var(--border);
    margin-top: 32px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# AUTO REFRESH – 5 seconds
# -----------------------------
st_autorefresh(interval=5000, key="live_refresh")

# -----------------------------
# DATASET
# -----------------------------
PRODUCTS = {
    "Apple MacBook Pro":     [120000, 180000, 220000],
    "iPhone 15 Pro":         [90000,  120000, 150000],
    "Samsung Galaxy S24":    [80000,  100000, 130000],
    "Dell XPS Laptop":       [95000,  140000, 170000],
    "LG OLED TV":            [60000,  85000,  120000],
    "Sony WH-1000XM5":       [25000,  30000,  40000],
    "HP Pavilion":           [55000,  75000,  90000],
    "Lenovo ThinkPad X1":    [110000, 150000, 190000],
    "Whirlpool AC":          [35000,  50000,  70000],
    "Bosch Washing Machine": [30000,  45000,  65000],
    "Canon DSLR":            [50000,  80000,  120000],
    "Boat Speaker":          [3000,   6000,   12000],
}
CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune"]

CITY_COLORS = {
    "Chennai":   "#3b82f6",
    "Mumbai":    "#06b6d4",
    "Bangalore": "#10b981",
    "Delhi":     "#f59e0b",
    "Hyderabad": "#8b5cf6",
    "Pune":      "#f43f5e",
}

# -----------------------------
# SESSION STATE
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "product", "city", "price"])

def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    return {
        "time":    datetime.now(),
        "product": product,
        "city":    random.choice(CITIES),
        "price":   random.choice(PRODUCTS[product]),
    }

def add_sale():
    new = pd.DataFrame([generate_sale()])
    st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
    if len(st.session_state.df) > 400:
        st.session_state.df = st.session_state.df.tail(400)

add_sale()

df = st.session_state.df.copy()
df["time"] = pd.to_datetime(df["time"])
df["year"] = df["time"].dt.year

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.markdown("### 🎛️ Dashboard Filters")
city_f    = st.sidebar.multiselect("🏙️ Cities",   CITIES,               default=CITIES)
product_f = st.sidebar.multiselect("📦 Products", list(PRODUCTS.keys()), default=list(PRODUCTS.keys()))
year_f    = st.sidebar.multiselect("📅 Year",     sorted(df["year"].unique()), default=list(df["year"].unique()))

df = df[
    (df["city"].isin(city_f)) &
    (df["product"].isin(product_f)) &
    (df["year"].isin(year_f))
]
merged = df.copy()

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    '<span class="pulse-dot"></span>'
    '<span style="font-size:11px;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">LIVE</span>',
    unsafe_allow_html=True
)
st.title("Enterprise Revenue Control Room")
st.markdown(
    f'<p style="color:#475569;font-size:13px;margin-top:-8px;">'
    f'Last updated: {datetime.now().strftime("%d %b %Y  •  %H:%M:%S")}</p>',
    unsafe_allow_html=True
)

# -----------------------------
# KPI CARDS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

total_rev  = merged["price"].sum()
total_ord  = len(merged)
avg_order  = merged["price"].mean() if total_ord else 0
city_count = merged["city"].nunique()

with c1:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <span class="kpi-icon">💰</span>
        <div class="kpi-title">Total Revenue</div>
        <div class="kpi-value">₹{total_rev:,.0f}</div>
        <div class="kpi-sub">Across all regions</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <span class="kpi-icon">📦</span>
        <div class="kpi-title">Total Orders</div>
        <div class="kpi-value">{total_ord:,}</div>
        <div class="kpi-sub">Transactions processed</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card kpi-amber">
        <span class="kpi-icon">📊</span>
        <div class="kpi-title">Avg Order Value</div>
        <div class="kpi-value">₹{avg_order:,.0f}</div>
        <div class="kpi-sub">Per transaction avg</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card kpi-purple">
        <span class="kpi-icon">🏙️</span>
        <div class="kpi-title">Active Cities</div>
        <div class="kpi-value">{city_count}</div>
        <div class="kpi-sub">Markets contributing</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =====================================================================
# ROW 1 – City Performance (Horizontal Bar)  |  Revenue Donut
# =====================================================================
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("🏙️ City Performance")
    city_df = (
        merged.groupby("city", as_index=False)["price"]
        .sum()
        .sort_values("price", ascending=True)
    )
    bar_colors = [CITY_COLORS.get(c, "#3b82f6") for c in city_df["city"]]

    fig_city = go.Figure(go.Bar(
        x=city_df["price"],
        y=city_df["city"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=[f"  ₹{v:,.0f}" for v in city_df["price"]],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig_city.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=80, t=10, b=10),
        height=320,
        xaxis=dict(
            showgrid=True, gridcolor="#1f2d45", gridwidth=1,
            zeroline=False, showticklabels=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#94a3b8", size=12),
            showgrid=False,
        ),
        showlegend=False,
        bargap=0.38,
    )
    st.plotly_chart(fig_city, use_container_width=True)

with col_right:
    st.subheader("🥇 Revenue Split")
    prod_pie = (
        merged.groupby("product", as_index=False)["price"]
        .sum()
        .sort_values("price", ascending=False)
        .head(6)
    )
    donut_colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#f43f5e"]

    fig_donut = go.Figure(go.Pie(
        labels=prod_pie["product"],
        values=prod_pie["price"],
        hole=0.55,
        marker=dict(colors=donut_colors, line=dict(color="#0b0f1a", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    total_l = prod_pie["price"].sum()
    fig_donut.add_annotation(
        text=f"<b>₹{total_l/1e5:.1f}L</b>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#60a5fa", family="Rajdhani"),
    )
    fig_donut.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=320,
        legend=dict(
            font=dict(color="#94a3b8", size=10),
            bgcolor="rgba(0,0,0,0)",
            x=1, y=0.5,
        ),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =====================================================================
# ROW 2 – Product Performance (Gradient Rounded Bars)
# =====================================================================
st.subheader("📦 Product Performance")

prod_df = (
    merged.groupby("product", as_index=False)["price"]
    .sum()
    .sort_values("price", ascending=False)
)
n = len(prod_df)

# Blue → Cyan gradient per bar based on rank
def lerp_color(t):
    r = int(59  + (6   - 59)  * t)
    g = int(130 + (182 - 130) * t)
    b = int(246 + (212 - 246) * t)
    return f"rgba({r},{g},{b},0.88)"

bar_colors_prod = [lerp_color(i / max(n - 1, 1)) for i in range(n)]

fig_prod = go.Figure(go.Bar(
    x=prod_df["product"],
    y=prod_df["price"],
    marker=dict(color=bar_colors_prod, line=dict(width=0)),
    text=[f"₹{v/1000:.0f}K" for v in prod_df["price"]],
    textposition="outside",
    textfont=dict(color="#94a3b8", size=10),
    hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
))
fig_prod.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=90),
    height=350,
    xaxis=dict(
        tickangle=-35,
        tickfont=dict(color="#64748b", size=10),
        showgrid=False, zeroline=False,
    ),
    yaxis=dict(
        showgrid=True, gridcolor="#1a2236", gridwidth=1,
        zeroline=False,
        tickfont=dict(color="#475569", size=10),
        tickformat=",.0f",
    ),
    bargap=0.3,
    showlegend=False,
)
st.plotly_chart(fig_prod, use_container_width=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =====================================================================
# ROW 3 – Revenue Trend (Glowing Area Chart)
# =====================================================================
st.subheader("📈 Revenue Trend")

trend = (
    merged.set_index("time")
    .resample("1min")["price"]
    .sum()
    .reset_index()
)
trend.columns = ["time", "revenue"]

fig_trend = go.Figure()

# Shaded area
fig_trend.add_trace(go.Scatter(
    x=trend["time"], y=trend["revenue"],
    fill="tozeroy",
    fillcolor="rgba(59,130,246,0.07)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=False,
    hoverinfo="skip",
))

# Glowing main line
fig_trend.add_trace(go.Scatter(
    x=trend["time"], y=trend["revenue"],
    mode="lines+markers",
    line=dict(color="#3b82f6", width=2.5),
    marker=dict(
        size=6,
        color="#06b6d4",
        line=dict(color="#0b0f1a", width=1.5),
    ),
    hovertemplate="<b>%{x|%H:%M}</b><br>₹%{y:,.0f}<extra></extra>",
    name="Revenue",
))

fig_trend.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    height=280,
    xaxis=dict(
        showgrid=True, gridcolor="#1a2236", gridwidth=1,
        zeroline=False,
        tickfont=dict(color="#475569", size=10),
    ),
    yaxis=dict(
        showgrid=True, gridcolor="#1a2236", gridwidth=1,
        zeroline=False,
        tickfont=dict(color="#475569", size=10),
        tickformat=",.0f",
    ),
    showlegend=False,
    hovermode="x unified",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =====================================================================
# ROW 4 – Live Transactions Table
# =====================================================================
st.subheader("🛰️ Live Transactions")

live_df = (
    merged
    .sort_values("time", ascending=False)
    .head(20)
    .copy()
)
live_df["time"]  = live_df["time"].dt.strftime("%H:%M:%S")
live_df["price"] = live_df["price"].apply(lambda x: f"₹{x:,.0f}")
live_df = live_df.rename(columns={
    "time":    "⏱ Time",
    "product": "📦 Product",
    "city":    "🏙️ City",
    "price":   "💰 Amount",
})
live_df = live_df[["⏱ Time", "📦 Product", "🏙️ City", "💰 Amount"]]

st.dataframe(live_df, use_container_width=True, hide_index=True)

# =====================================================================
# FOOTER
# =====================================================================
st.markdown(
    '<div class="footer">'
    '⚡ Enterprise Revenue Control Room &nbsp;•&nbsp; '
    'Auto-refreshes every 5s &nbsp;•&nbsp; '
    'Professional Analytics Platform'
    '</div>',
    unsafe_allow_html=True
)
