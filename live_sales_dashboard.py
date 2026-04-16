import random
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import requests

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise Revenue Intelligence", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #1e1e1e;
    color: #f5f5f5;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
""", unsafe_allow_html=True)

REFRESH_MS = 5000
MAX_ROWS = 300

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USERS = {"admin": "admin123", "viewer": "viewer123"}

if "auth" not in st.session_state:
    st.session_state.auth = None

if not st.session_state.auth:
    st.title("🔐 Enterprise Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and USERS[u] == p:
            st.session_state.auth = u
            st.rerun()
        else:
            st.error("Invalid login")
    st.stop()

ROLE = "admin" if st.session_state.auth == "admin" else "viewer"
st.sidebar.success(f"{st.session_state.auth} ({ROLE})")

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=REFRESH_MS, key="live")

# -----------------------------
# PROFESSIONAL PRODUCT DATASET (NEW)
# -----------------------------
PRODUCTS = {
    "Apple MacBook Pro": [120000, 180000, 220000],
    "iPhone 15 Pro": [90000, 120000, 150000],
    "Samsung Galaxy S24": [80000, 100000, 130000],
    "Dell XPS Laptop": [95000, 140000, 170000],
    "LG Smart TV 55”": [60000, 85000, 120000],
    "Sony WH-1000XM5": [25000, 30000, 40000],
    "HP Pavilion Laptop": [55000, 75000, 90000],
    "Lenovo ThinkPad X1": [110000, 150000, 190000],
    "Whirlpool AC 1.5T": [35000, 50000, 70000],
    "Bosch Washing Machine": [30000, 45000, 65000],
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
            params={"latitude": lat, "longitude": lon, "current": "temperature_2m,weather_code"},
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

    if len(st.session_state.df) > MAX_ROWS:
        st.session_state.df = st.session_state.df.tail(MAX_ROWS)

add_sale()

df = st.session_state.df.copy()
df["time"] = pd.to_datetime(df["time"])
df["year"] = df["time"].dt.year

weather = pd.DataFrame([get_weather(c) for c in CITIES])

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Enterprise Revenue Intelligence (Control Room View)")
st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Revenue", f"₹{df['price'].sum():,.0f}")
col2.metric("📦 Orders", len(df))
col3.metric("📊 Avg Order", f"₹{df['price'].mean():,.0f}" if len(df) else "₹0")

# -----------------------------
# CITY PERFORMANCE
# -----------------------------
st.subheader("🏙️ City Performance")

city_df = df.groupby("city", as_index=False)["price"].sum().sort_values("price", ascending=False)

fig1 = px.bar(city_df, x="city", y="price", text="price", color="price")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# PRODUCT PERFORMANCE
# -----------------------------
st.subheader("📦 Enterprise Product Performance (Top Devices)")

prod_df = df.groupby("product", as_index=False)["price"].sum().sort_values("price", ascending=False)

fig2 = px.bar(prod_df, x="product", y="price", text="price", color="price")
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# WEATHER IMPACT
# -----------------------------
st.subheader("🌦️ Weather Impact Analysis")

merged = df.merge(weather, on="city", how="left")

weather_df = merged.groupby("impact", as_index=False)["price"].sum()

fig3 = px.pie(weather_df, names="impact", values="price", hole=0.5)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TREND
# -----------------------------
st.subheader("📈 Revenue Trend")

trend = df.set_index("time").resample("1min")["price"].sum().reset_index()

fig4 = px.line(trend, x="time", y="price", markers=True)
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# LIVE TABLE
# -----------------------------
st.subheader("🛰️ Live Transaction Feed")

st.dataframe(
    df.sort_values("time", ascending=False).head(15),
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚡ Enterprise Control Room: Dark Mode + Premium Products + Real-time Analytics")
