import random
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Live Secure Revenue Pulse", layout="wide")

REFRESH_MS = 5000
MAX_ROWS = 300

# -----------------------------
# ROLE SYSTEM (SIMPLIFIED)
# -----------------------------
USERS = {
    "admin": "admin123",
    "viewer": "viewer123"
}

if "auth" not in st.session_state:
    st.session_state.auth = None

# -----------------------------
# LOGIN
# -----------------------------
if not st.session_state.auth:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.auth = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

ROLE = "admin" if st.session_state.auth == "admin" else "viewer"

st.sidebar.success(f"Logged in as: {st.session_state.auth} ({ROLE})")

# -----------------------------
# AUTO REFRESH (5 seconds)
# -----------------------------
st_autorefresh(interval=REFRESH_MS, key="live_refresh")

# -----------------------------
# SESSION DATA
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["time", "product", "city", "price"])

PRODUCTS = ["Laptop", "Phone", "Tablet", "Watch"]
CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi"]

# -----------------------------
# GENERATE LIVE DATA SAFELY
# -----------------------------
def generate_sale():
    return {
        "time": datetime.now(),
        "product": random.choice(PRODUCTS),
        "city": random.choice(CITIES),
        "price": random.randint(5000, 90000),
    }

def add_sale():
    new_row = pd.DataFrame([generate_sale()])
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

    # memory control (important for security/stability)
    if len(st.session_state.df) > MAX_ROWS:
        st.session_state.df = st.session_state.df.tail(MAX_ROWS)

# Add new data every refresh
add_sale()

df = st.session_state.df.copy()
df["time"] = pd.to_datetime(df["time"])

# -----------------------------
# UI HEADER
# -----------------------------
st.title("📊 Live Revenue Command Center (5s Secure Stream)")

st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"₹{df['price'].sum():,.0f}")
col2.metric("📦 Orders", len(df))
col3.metric("📊 Avg Order", f"₹{df['price'].mean():,.0f}" if len(df) else "₹0")

# -----------------------------
# REVENUE BY CITY
# -----------------------------
st.subheader("🏙️ Revenue by City")

city_df = df.groupby("city", as_index=False)["price"].sum()

fig = px.bar(city_df, x="city", y="price", text="price")
fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# LIVE TREND (5 MIN WINDOW)
# -----------------------------
st.subheader("📈 Live Revenue Trend")

trend = df.set_index("time").resample("1min")["price"].sum().reset_index()

fig2 = px.line(trend, x="time", y="price", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# PRODUCT MIX
# -----------------------------
st.subheader("🛍️ Product Mix")

pie = df.groupby("product", as_index=False)["price"].sum()

fig3 = px.pie(pie, names="product", values="price", hole=0.5)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# LIVE TABLE
# -----------------------------
st.subheader("🛰️ Live Feed")

show = df.sort_values("time", ascending=False).head(10)
st.dataframe(show, use_container_width=True, hide_index=True)

# -----------------------------
# SECURITY NOTE
# -----------------------------
st.caption("🔐 Secure Mode: session-based auth + bounded memory + auto-refresh 5s")
