import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Enterprise Live Revenue Pulse",
    layout="wide",
    page_icon="📊"
)

st.title("🚀 Enterprise Live Revenue Pulse Dashboard")

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = True

if "last_revenue" not in st.session_state:
    st.session_state.last_revenue = 0

# -------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------
st.sidebar.header("⚙️ Controls")

st.session_state.running = st.sidebar.toggle("▶️ Run Simulation", value=True)

refresh_rate = st.sidebar.slider("⏱ Refresh Speed (seconds)", 5, 60, 15)

city_filter = st.sidebar.multiselect(
    "🏙 Filter City",
    ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune"],
    default=[]
)

weather_filter = st.sidebar.multiselect(
    "🌦 Filter Weather",
    ["Rain 🌧️", "Cloudy ☁️", "Heat ☀️", "Normal 🌤️", "Unknown"],
    default=[]
)

# Auto refresh only if running
if st.session_state.running:
    st_autorefresh(interval=refresh_rate * 1000, key="refresh")

# -------------------------------------------------
# DATABASE (cached connection)
# -------------------------------------------------
@st.cache_resource
def get_db():
    conn = sqlite3.connect("sales.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        product TEXT,
        price REAL,
        city TEXT,
        weather TEXT
    )
    """)
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# -------------------------------------------------
# DATA CONFIG
# -------------------------------------------------
products = ["Laptop","Mobile","Headphones","Keyboard","Monitor","Mouse","Tablet","Smart Watch"]
cities = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi","Pune"]
prices = [25000,35000,1500,2000,12000,800,22000,7000]

# -------------------------------------------------
# WEATHER API (safe)
# -------------------------------------------------
@st.cache_data(ttl=300)
def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=3)
        data = r.json()
        condition = data["current_condition"][0]["weatherDesc"][0]["value"].lower()

        if "rain" in condition:
            return "Rain 🌧️"
        elif "cloud" in condition:
            return "Cloudy ☁️"
        elif "sun" in condition:
            return "Heat ☀️"
        return "Normal 🌤️"
    except:
        return "Unknown"

# -------------------------------------------------
# GENERATE SALE (controlled)
# -------------------------------------------------
def generate_sale():
    product = random.choice(products)
    price = random.choice(prices)
    city = random.choice(cities)
    weather = get_weather(city)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO sales(time,product,price,city,weather) VALUES(?,?,?,?,?)",
        (time_now, product, price, city, weather)
    )
    conn.commit()

if st.session_state.running:
    generate_sale()

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = pd.read_sql("SELECT * FROM sales", conn)

df["time"] = pd.to_datetime(df["time"], errors="coerce")

# Apply filters
if city_filter:
    df = df[df["city"].isin(city_filter)]

if weather_filter:
    df = df[df["weather"].isin(weather_filter)]

# -------------------------------------------------
# KPI METRICS (with delta)
# -------------------------------------------------
total_revenue = df["price"].sum()
total_orders = len(df)
avg_order = df["price"].mean() if total_orders > 0 else 0

delta = total_revenue - st.session_state.last_revenue
st.session_state.last_revenue = total_revenue

c1, c2, c3 = st.columns(3)

c1.metric("💰 Revenue", f"₹{int(total_revenue):,}", f"{int(delta):,}")
c2.metric("📦 Orders", total_orders)
c3.metric("📊 Avg Order", f"₹{int(avg_order):,}")

st.divider()

# -------------------------------------------------
# EXPORT DATA
# -------------------------------------------------
st.download_button(
    "⬇️ Export Data",
    data=df.to_csv(index=False),
    file_name="sales_data.csv",
    mime="text/csv"
)

# -------------------------------------------------
# LIVE FEED
# -------------------------------------------------
st.subheader("🟢 Live Sales Feed")

st.dataframe(df.sort_values("id", ascending=False).head(15), use_container_width=True)

# -------------------------------------------------
# CHARTS
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Revenue by City")
    city_chart = df.groupby("city")["price"].sum().reset_index()

    fig = px.bar(city_chart, x="city", y="price", text="price")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌦 Weather Impact")
    weather_chart = df.groupby("weather")["price"].sum().reset_index()

    fig2 = px.pie(weather_chart, names="weather", values="price")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# TREND ANALYSIS
# -------------------------------------------------
st.subheader("📊 Sales Trend")

if not df.empty:
    trend = df.set_index("time").resample("1min")["price"].sum()

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=trend.index,
        y=trend.values,
        mode="lines+markers"
    ))

    st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------
# CITY + WEATHER TABLE
# -------------------------------------------------
st.subheader("🌍 City Weather Matrix")
st.dataframe(df.groupby(["city", "weather"]).size().reset_index(name="count"))

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")