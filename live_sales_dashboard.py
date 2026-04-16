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
st.set_page_config(page_title="Live Secure Revenue Pulse", layout="wide")

REFRESH_MS = 5000
MAX_ROWS = 300

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USERS = {"admin": "admin123", "viewer": "viewer123"}

if "auth" not in st.session_state:
    st.session_state.auth = None

if not st.session_state.auth:
    st.title("🔐 Login")

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
# ELECTRONICS + APPLIANCES DATASET (EXPANDED)
# -----------------------------
PRODUCTS = {
    "Laptop": [45000, 65000, 85000],
    "Phone": [12000, 18000, 25000],
    "Tablet": [15000, 22000, 30000],
    "Smartwatch": [3000, 6000, 9000],
    "Headphones": [2000, 3500, 5000],
    "TV": [25000, 40000, 80000],
    "Refrigerator": [18000, 35000, 60000],
    "Washing Machine": [15000, 30000, 55000],
    "Microwave": [5000, 12000, 20000],
    "AC": [25000, 45000, 70000],
    "Bluetooth Speaker": [1500, 4000, 8000],
    "Camera DSLR": [35000, 50000, 90000],
}

CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune"]

# -----------------------------
# WEATHER API (Open-Meteo)
# -----------------------------
CITY_COORDS = {
    "Chennai": (13.08, 80.27),
    "Mumbai": (19.07, 72.87),
    "Bangalore": (12.97, 77.59),
    "Delhi": (28.61, 77.20),
    "Hyderabad": (17.38, 78.48),
    "Pune": (18.52, 73.85),
}

@st.cache_data(ttl=600)
def get_weather(city):
    try:
        lat, lon = CITY_COORDS[city]
        url = "https://api.open-meteo.com/v1/forecast"
        r = requests.get(url, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code"
        }, timeout=5)

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
    price = random.choice(PRODUCTS[product])

    return {
        "time": datetime.now(),
        "product": product,
        "city": random.choice(CITIES),
        "price": price,
    }

def add_sale():
    new = pd.DataFrame([generate_sale()])
    st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)

    if len(st.session_state.df) > MAX_ROWS:
        st.session_state.df = st.session_state.df.tail(MAX_ROWS)

add_sale()

df = st.session_state.df.copy()
df["time"] = pd.to_datetime(df["time"])

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Enterprise Live Revenue + Weather Intelligence")

st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Revenue", f"₹{df['price'].sum():,.0f}")
col2.metric("📦 Orders", len(df))
col3.metric("📊 Avg Order", f"₹{df['price'].mean():,.0f}")

# -----------------------------
# WEATHER PANEL
# -----------------------------
st.subheader("🌦️ City Weather Intelligence")

weather_data = [get_weather(c) for c in CITIES]
wdf = pd.DataFrame(weather_data)

st.dataframe(wdf, use_container_width=True)

# -----------------------------
# REVENUE BY CITY
# -----------------------------
st.subheader("🏙️ Revenue by City")

city_df = df.groupby("city", as_index=False)["price"].sum()

fig = px.bar(city_df, x="city", y="price", text="price")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PRODUCT MIX
# -----------------------------
st.subheader("⚡ Electronics & Appliances Mix")

product_df = df.groupby("product", as_index=False)["price"].sum()

fig2 = px.pie(product_df, names="product", values="price", hole=0.5)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# WEATHER IMPACT INSIGHT
# -----------------------------
st.subheader("📡 Weather Impact Insight")

merged = df.merge(wdf, on="city", how="left")

impact_summary = merged.groupby("impact", as_index=False)["price"].sum()

fig3 = px.bar(impact_summary, x="impact", y="price", text="price")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# LIVE FEED
# -----------------------------
st.subheader("🛰️ Live Sales Feed")

st.dataframe(df.sort_values("time", ascending=False).head(10),
             use_container_width=True,
             hide_index=True)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚡ Enterprise Mode: Weather + Electronics + Live Stream + Secure Auth")
