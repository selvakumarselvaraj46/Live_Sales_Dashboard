import random
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import requests
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
# PROFESSIONAL DARK THEME
# -----------------------------
st.markdown("""
<style>
/* Main Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
}

/* Remove header background */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #020617;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #334155;
    box-shadow: 0 0 15px rgba(59,130,246,0.2);
    text-align: center;
}

.kpi-title {
    font-size: 14px;
    color: #94a3b8;
}

.kpi-value {
    font-size: 26px;
    font-weight: bold;
    color: #38bdf8;
}

/* Section Titles */
h2, h3 {
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=5000, key="live")

# -----------------------------
# DATASET
# -----------------------------
PRODUCTS = {
    "Apple MacBook Pro": [120000, 180000, 220000],
    "iPhone 15 Pro": [90000, 120000, 150000],
    "Samsung Galaxy S24": [80000, 100000, 130000],
    "Dell XPS Laptop": [95000, 140000, 170000],
    "LG OLED TV": [60000, 85000, 120000],
    "Sony WH-1000XM5": [25000, 30000, 40000],
    "HP Pavilion": [55000, 75000, 90000],
    "Lenovo ThinkPad X1": [110000, 150000, 190000],
    "Whirlpool AC": [35000, 50000, 70000],
    "Bosch Washing Machine": [30000, 45000, 65000],
    "Canon DSLR": [50000, 80000, 120000],
    "Boat Speaker": [3000, 6000, 12000],
}

CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune"]

CITY_COORDS = {
    "Chennai": (13.08, 80.27),
    "Mumbai": (19.07, 72.87),
    "Bangalore": (12.97, 77.59),
    "Delhi": (28.61, 77.20),
    "Hyderabad": (17.38, 78.48),
    "Pune": (18.52, 73.85),
}

# -----------------------------
# WEATHER API
# -----------------------------
@st.cache_data(ttl=600)
def get_weather(city):
    try:
        lat, lon = CITY_COORDS[city]
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code"
            },
            timeout=5
        )
        data = r.json()["current"]
        temp = data["temperature_2m"]
        code = data["weather_code"]

        if temp > 35:
            impact = "Heat"
        elif code in [51, 61, 63, 65, 80]:
            impact = "Rain"
        else:
            impact = "Normal"

        return {"city": city, "temp": temp, "impact": impact}
    except:
        return {"city": city, "temp": None, "impact": "Unknown"}

# -----------------------------
# SESSION DATA
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "product", "city", "price"])

def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    return {
        "time": datetime.now(),
        "product": product,
        "city": random.choice(CITIES),
        "price": random.choice(PRODUCTS[product]),
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

weather = pd.DataFrame([get_weather(c) for c in CITIES])

# -----------------------------
# FILTERS
# -----------------------------
st.title("📊 Enterprise Control Room – Revenue Intelligence")

st.sidebar.header("🎛️ Filters")

city_f = st.sidebar.multiselect("Cities", CITIES, default=CITIES)
product_f = st.sidebar.multiselect("Products", list(PRODUCTS.keys()), default=list(PRODUCTS.keys()))
year_f = st.sidebar.multiselect("Year", sorted(df["year"].unique()), default=list(df["year"].unique()))
weather_f = st.sidebar.multiselect("Weather", ["Heat", "Rain", "Normal", "Unknown"], default=["Heat","Rain","Normal","Unknown"])

df = df[
    (df["city"].isin(city_f)) &
    (df["product"].isin(product_f)) &
    (df["year"].isin(year_f))
]

merged = df.merge(weather, on="city", how="left")
merged = merged[merged["impact"].isin(weather_f)]

# -----------------------------
# KPI CARDS (CUSTOM)
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

def kpi(label, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

with col1:
    kpi("💰 Revenue", f"₹{merged['price'].sum():,.0f}")

with col2:
    kpi("📦 Orders", f"{len(merged)}")

with col3:
    avg = merged['price'].mean() if len(merged) else 0
    kpi("📊 Avg Order", f"₹{avg:,.0f}")

with col4:
    kpi("🏙️ Cities", merged["city"].nunique())

st.markdown("---")

# -----------------------------
# COLOR PALETTE
# -----------------------------
colors = ["#38bdf8", "#6366f1", "#22c55e", "#f59e0b", "#ef4444"]

# -----------------------------
# VISUALS
# -----------------------------
st.subheader("🏙️ City Performance")

city_df = merged.groupby("city", as_index=False)["price"].sum()

fig1 = px.bar(city_df, x="city", y="price",
              color="price",
              color_continuous_scale="Blues")

fig1.update_layout(template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
st.subheader("📦 Product Performance")

prod_df = merged.groupby("product", as_index=False)["price"].sum()

fig2 = px.bar(prod_df, x="product", y="price",
              color="price",
              color_continuous_scale="Viridis")

fig2.update_layout(template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
st.subheader("🌦️ Weather Impact")

weather_df = merged.groupby("impact", as_index=False)["price"].sum()

fig3 = px.pie(weather_df, names="impact", values="price",
              color_discrete_sequence=colors)

fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
st.subheader("📈 Revenue Trend")

trend = merged.set_index("time").resample("1min")["price"].sum().reset_index()

fig4 = px.line(trend, x="time", y="price",
               markers=True)

fig4.update_traces(line=dict(color="#38bdf8", width=3))
fig4.update_layout(template="plotly_dark")

st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------
st.subheader("🛰️ Live Transactions")

st.dataframe(
    merged.sort_values("time", ascending=False).head(20),
    use_container_width=True
)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚡ Enterprise Dashboard • Professional UI • Live Data • Weather Intelligence")
