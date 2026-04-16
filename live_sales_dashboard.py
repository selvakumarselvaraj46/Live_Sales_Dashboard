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
# PRODUCT MASTER (WITH BRAND + CATEGORY)
# -----------------------------
PRODUCTS = {
    "Apple MacBook Pro":     {"brand": "Apple",    "category": "Laptop",      "price": [120000,180000,220000]},
    "iPhone 15 Pro":         {"brand": "Apple",    "category": "Mobile",      "price": [90000,120000,150000]},
    "Samsung Galaxy S24":    {"brand": "Samsung",  "category": "Mobile",      "price": [80000,100000,130000]},
    "Dell XPS Laptop":       {"brand": "Dell",     "category": "Laptop",      "price": [95000,140000,170000]},
    "LG OLED TV":            {"brand": "LG",       "category": "Television",  "price": [60000,85000,120000]},
    "Sony WH-1000XM5":       {"brand": "Sony",     "category": "Audio",       "price": [25000,30000,40000]},
    "HP Pavilion":           {"brand": "HP",       "category": "Laptop",      "price": [55000,75000,90000]},
    "Lenovo ThinkPad X1":    {"brand": "Lenovo",   "category": "Laptop",      "price": [110000,150000,190000]},
    "Whirlpool AC":          {"brand": "Whirlpool","category": "Appliance",   "price": [35000,50000,70000]},
    "Bosch Washing Machine": {"brand": "Bosch",    "category": "Appliance",   "price": [30000,45000,65000]},
    "Canon DSLR":            {"brand": "Canon",    "category": "Camera",      "price": [50000,80000,120000]},
    "Boat Speaker":          {"brand": "Boat",     "category": "Audio",       "price": [3000,6000,12000]},
}

CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune"]

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=5000, key="live_refresh")

# -----------------------------
# SESSION STATE
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=["time","product","brand","category","city","price"]
    )

def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    prod_info = PRODUCTS[product]
    return {
        "time": datetime.now(),
        "product": product,
        "brand": prod_info["brand"],
        "category": prod_info["category"],
        "city": random.choice(CITIES),
        "price": random.choice(prod_info["price"]),
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
st.sidebar.title("🎛️ Filters")

city_f = st.sidebar.multiselect("City", df["city"].unique(), default=df["city"].unique())
product_f = st.sidebar.multiselect("Product", df["product"].unique(), default=df["product"].unique())
brand_f = st.sidebar.multiselect("Brand", df["brand"].unique(), default=df["brand"].unique())
category_f = st.sidebar.multiselect("Category", df["category"].unique(), default=df["category"].unique())
year_f = st.sidebar.multiselect("Year", df["year"].unique(), default=df["year"].unique())

df = df[
    (df["city"].isin(city_f)) &
    (df["product"].isin(product_f)) &
    (df["brand"].isin(brand_f)) &
    (df["category"].isin(category_f)) &
    (df["year"].isin(year_f))
]

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Enterprise Revenue Control Room")
st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}")

# -----------------------------
# KPI
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

total_rev = df["price"].sum()
total_orders = len(df)
avg_order = df["price"].mean() if total_orders else 0
cities = df["city"].nunique()

col1.metric("Total Revenue", f"₹{total_rev:,.0f}")
col2.metric("Orders", total_orders)
col3.metric("Avg Order", f"₹{avg_order:,.0f}")
col4.metric("Cities", cities)

# -----------------------------
# CITY CHART
# -----------------------------
st.subheader("🏙️ City Performance")

city_df = df.groupby("city")["price"].sum().reset_index()

fig = go.Figure(go.Bar(
    x=city_df["price"],
    y=city_df["city"],
    orientation="h"
))
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PRODUCT CHART
# -----------------------------
st.subheader("📦 Product Performance")

prod_df = df.groupby("product")["price"].sum().reset_index()

fig2 = go.Figure(go.Bar(
    x=prod_df["product"],
    y=prod_df["price"]
))
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TREND
# -----------------------------
st.subheader("📈 Revenue Trend")

trend = df.set_index("time").resample("1min")["price"].sum().reset_index()

fig3 = go.Figure(go.Scatter(
    x=trend["time"],
    y=trend["price"],
    mode="lines+markers"
))
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------
st.subheader("🛰️ Live Transactions")

live_df = df.sort_values("time", ascending=False).head(20)
st.dataframe(live_df, use_container_width=True)
