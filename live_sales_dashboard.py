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

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: #0f1117;
    color: #e6e6e6;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
.block {
    background: #161a25;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #2a2f3a;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=5000, key="live")

# -----------------------------
# DATASET (10+ PREMIUM PRODUCTS)
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
# FILTERS (HIGH CONFIG)
# -----------------------------
st.title("📊 Enterprise Control Room – Revenue Intelligence")

st.sidebar.header("🎛️ Advanced Filters")

city_f = st.sidebar.multiselect("Cities", CITIES, default=CITIES)
product_f = st.sidebar.multiselect("Products", list(PRODUCTS.keys()), default=list(PRODUCTS.keys()))
year_f = st.sidebar.multiselect("Year", sorted(df["year"].unique()), default=list(df["year"].unique()))
weather_f = st.sidebar.multiselect("Weather", ["Heat", "Rain", "Normal", "Unknown"], default=["Heat","Rain","Normal","Unknown"])

# -----------------------------
# APPLY FILTERS
# -----------------------------
df = df[
    (df["city"].isin(city_f)) &
    (df["product"].isin(product_f)) &
    (df["year"].isin(year_f))
]

merged = df.merge(weather, on="city", how="left")
merged = merged[merged["impact"].isin(weather_f)]

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"₹{merged['price'].sum():,.0f}")
col2.metric("📦 Orders", len(merged))
col3.metric("📊 Avg Order", f"₹{merged['price'].mean():,.0f}" if len(merged) else "₹0")
col4.metric("🏙️ Active Cities", merged["city"].nunique())

st.markdown("---")

# -----------------------------
# VISUAL 1 - CITY PERFORMANCE
# -----------------------------
st.subheader("🏙️ City Intelligence Matrix")

city_df = merged.groupby("city", as_index=False)["price"].sum().sort_values("price", ascending=False)

fig1 = px.bar(city_df, x="city", y="price", color="price", text="price")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# VISUAL 2 - PRODUCT PERFORMANCE
# -----------------------------
st.subheader("📦 Product Revenue Engine")

prod_df = merged.groupby("product", as_index=False)["price"].sum().sort_values("price", ascending=False)

fig2 = px.bar(prod_df, x="product", y="price", color="price", text="price")
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# VISUAL 3 - WEATHER IMPACT
# -----------------------------
st.subheader("🌦️ Weather Intelligence Layer")

weather_df = merged.groupby("impact", as_index=False)["price"].sum()

fig3 = px.pie(weather_df, names="impact", values="price", hole=0.55)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# VISUAL 4 - TREND ENGINE
# -----------------------------
st.subheader("📈 Real-Time Revenue Stream")

trend = merged.set_index("time").resample("1min")["price"].sum().reset_index()

fig4 = px.line(trend, x="time", y="price", markers=True)
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# LIVE TABLE
# -----------------------------
st.subheader("🛰️ Live Transaction Feed")

st.dataframe(
    merged.sort_values("time", ascending=False).head(20),
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚡ Enterprise Grade Dashboard: Filters + Weather AI + Product Intelligence + Live Stream (5s)")
