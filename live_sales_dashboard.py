import random
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Human Revenue Command Center", layout="wide")

REFRESH_MS = 5000
SALE_INTERVAL_SECONDS = 20
MAX_ROWS = 800

st_autorefresh(interval=REFRESH_MS, key="auto_refresh")

# -----------------------------
# DATA MODELS
# -----------------------------
PRODUCTS = {
    "Laptop": [45000, 65000, 85000],
    "Phone": [12000, 18000, 25000],
    "Tablet": [15000, 22000, 30000],
    "Headphones": [2000, 3500, 5000],
    "Smartwatch": [3000, 6000, 9000],
    "Speakers": [4500, 6000, 7500],
}

CITIES = ["Chennai", "Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune"]

# -----------------------------
# SESSION STATE
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "product", "price", "city", "persona"])

if "last_time" not in st.session_state:
    st.session_state.last_time = datetime.now()

# -----------------------------
# HUMAN PERSONA ENGINE
# -----------------------------
def generate_persona():
    personas = [
        "Tech Buyer 🧑‍💻",
        "Budget Shopper 💰",
        "Premium Customer 👑",
        "Student Buyer 🎓",
        "Business Buyer 📊",
        "Impulse Shopper ⚡"
    ]
    return random.choice(personas)

# -----------------------------
# SALES GENERATOR (HUMAN SIMULATION)
# -----------------------------
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    price = random.choice(PRODUCTS[product]) + random.randint(-1000, 2000)
    city = random.choice(CITIES)
    return {
        "time": datetime.now(),
        "product": product,
        "price": max(price, 500),
        "city": city,
        "persona": generate_persona()
    }

# -----------------------------
# AUTO DATA APPEND
# -----------------------------
now = datetime.now()
if (now - st.session_state.last_time).seconds >= SALE_INTERVAL_SECONDS:
    new_data = pd.DataFrame([generate_sale()])
    st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
    st.session_state.last_time = now

# limit rows
st.session_state.df = st.session_state.df.tail(MAX_ROWS)

df = st.session_state.df.copy()

# -----------------------------
# AI INSIGHTS ENGINE
# -----------------------------
def demand_index(city_df):
    if len(city_df) == 0:
        return 0
    return round((city_df["price"].sum() / len(city_df)) / 1000, 2)

def anomaly_detection(series):
    if len(series) < 5:
        return "Stable"
    mean = np.mean(series)
    last = series.iloc[-1]
    if last > mean * 1.5:
        return "🔥 Spike Detected"
    elif last < mean * 0.5:
        return "📉 Drop Detected"
    return "Stable"

# -----------------------------
# UI HEADER
# -----------------------------
st.title("🤖 Human + AI Revenue Command Center")
st.caption("Real-time Human behavior simulation + AI insights engine")

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

total_rev = df["price"].sum() if not df.empty else 0
orders = len(df)
avg_order = df["price"].mean() if not df.empty else 0
last_city = df["city"].iloc[-1] if not df.empty else "None"

with col1:
    st.metric("💰 Revenue", f"₹{total_rev:,.0f}")
with col2:
    st.metric("🧾 Orders", orders)
with col3:
    st.metric("📦 Avg Order", f"₹{avg_order:,.0f}")
with col4:
    st.metric("📍 Last City", last_city)

# -----------------------------
# CHART: CITY REVENUE
# -----------------------------
st.subheader("🏙️ City Intelligence Layer")

if not df.empty:
    city_df = df.groupby("city", as_index=False)["price"].sum()
    fig = px.bar(city_df, x="city", y="price", color="price", text="price")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# HUMAN BEHAVIOR VIEW
# -----------------------------
st.subheader("🧠 Human Behavior Simulation Feed")

if not df.empty:
    show = df.tail(10).copy()
    show["time"] = show["time"].dt.strftime("%H:%M:%S")
    st.dataframe(show, use_container_width=True)

# -----------------------------
# AI DEMAND ENGINE
# -----------------------------
st.subheader("📊 AI Demand Intelligence")

if not df.empty:
    demand_table = []
    for city in df["city"].unique():
        temp_df = df[df["city"] == city]
        demand_table.append({
            "City": city,
            "Demand Index": demand_index(temp_df),
            "Orders": len(temp_df),
            "Revenue": temp_df["price"].sum()
        })

    demand_df = pd.DataFrame(demand_table)
    st.dataframe(demand_df, use_container_width=True)

# -----------------------------
# PRODUCT INTELLIGENCE
# -----------------------------
st.subheader("🛍️ Product Intelligence")

if not df.empty:
    product_df = df.groupby("product", as_index=False)["price"].sum()
    fig2 = px.pie(product_df, names="product", values="price", hole=0.5)
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# ANOMALY DETECTION
# -----------------------------
st.subheader("⚡ AI Anomaly Detector")

if not df.empty:
    trend = df.groupby(pd.Grouper(key="time", freq="2min"))["price"].sum().reset_index()
    status = anomaly_detection(trend["price"])
    st.info(f"System Status: {status}")

# -----------------------------
# WEATHERLESS SMART INSIGHT
# -----------------------------
st.subheader("🧠 AI Recommendation Engine")

if not df.empty:
    top_product = df.groupby("product")["price"].sum().idxmax()
    top_city = df.groupby("city")["price"].sum().idxmax()

    st.success(f"🔥 Best Product: {top_product}")
    st.success(f"📍 Best City: {top_city}")
    st.info("💡 Suggestion: Increase ads targeting high-demand city-product pair")

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚡ Powered by Human Simulation AI + Streamlit Intelligence Engine")
