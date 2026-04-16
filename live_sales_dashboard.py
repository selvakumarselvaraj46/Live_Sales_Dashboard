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
st.markdown("""<style>
/* (UNCHANGED CSS — kept same as your code) */
</style>""", unsafe_allow_html=True)

# -----------------------------
# AUTO REFRESH – 5 seconds
# -----------------------------
st_autorefresh(interval=5000, key="live_refresh")

# -----------------------------
# DATASET (UPDATED WITH BRAND + CATEGORY)
# -----------------------------
PRODUCTS = {
    "Apple MacBook Pro":     {"brand":"Apple","category":"Laptop","price":[120000,180000,220000]},
    "iPhone 15 Pro":         {"brand":"Apple","category":"Mobile","price":[90000,120000,150000]},
    "Samsung Galaxy S24":    {"brand":"Samsung","category":"Mobile","price":[80000,100000,130000]},
    "Dell XPS Laptop":       {"brand":"Dell","category":"Laptop","price":[95000,140000,170000]},
    "LG OLED TV":            {"brand":"LG","category":"Television","price":[60000,85000,120000]},
    "Sony WH-1000XM5":       {"brand":"Sony","category":"Audio","price":[25000,30000,40000]},
    "HP Pavilion":           {"brand":"HP","category":"Laptop","price":[55000,75000,90000]},
    "Lenovo ThinkPad X1":    {"brand":"Lenovo","category":"Laptop","price":[110000,150000,190000]},
    "Whirlpool AC":          {"brand":"Whirlpool","category":"Appliance","price":[35000,50000,70000]},
    "Bosch Washing Machine": {"brand":"Bosch","category":"Appliance","price":[30000,45000,65000]},
    "Canon DSLR":            {"brand":"Canon","category":"Camera","price":[50000,80000,120000]},
    "Boat Speaker":          {"brand":"Boat","category":"Audio","price":[3000,6000,12000]},
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
# SESSION STATE (UPDATED COLUMNS)
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=["time", "product", "brand", "category", "city", "price"]
    )

def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    info = PRODUCTS[product]
    return {
        "time": datetime.now(),
        "product": product,
        "brand": info["brand"],
        "category": info["category"],
        "city": random.choice(CITIES),
        "price": random.choice(info["price"]),
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
# SIDEBAR FILTERS (ADDED BRAND + CATEGORY)
# -----------------------------
st.sidebar.markdown("### 🎛️ Dashboard Filters")

city_f = st.sidebar.multiselect("🏙️ Cities", CITIES, default=CITIES)
product_f = st.sidebar.multiselect("📦 Products", list(PRODUCTS.keys()), default=list(PRODUCTS.keys()))
brand_f = st.sidebar.multiselect("🏷️ Brand", df["brand"].unique(), default=df["brand"].unique())
category_f = st.sidebar.multiselect("📂 Category", df["category"].unique(), default=df["category"].unique())
year_f = st.sidebar.multiselect("📅 Year", sorted(df["year"].unique()), default=list(df["year"].unique()))

# -----------------------------
# FILTER LOGIC (UPDATED)
# -----------------------------
df = df[
    (df["city"].isin(city_f)) &
    (df["product"].isin(product_f)) &
    (df["brand"].isin(brand_f)) &
    (df["category"].isin(category_f)) &
    (df["year"].isin(year_f))
]

merged = df.copy()

# -----------------------------
# HEADER (UNCHANGED)
# -----------------------------
st.title("Enterprise Revenue Control Room")

# -----------------------------
# KPI (UNCHANGED)
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

total_rev = merged["price"].sum()
total_ord = len(merged)
avg_order = merged["price"].mean() if total_ord else 0
city_count = merged["city"].nunique()

c1.metric("Revenue", f"₹{total_rev:,.0f}")
c2.metric("Orders", total_ord)
c3.metric("Avg", f"₹{avg_order:,.0f}")
c4.metric("Cities", city_count)

# -----------------------------
# CITY CHART (UNCHANGED)
# -----------------------------
city_df = merged.groupby("city")["price"].sum().reset_index()

fig = go.Figure(go.Bar(
    x=city_df["price"],
    y=city_df["city"],
    orientation="h"
))
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PRODUCT CHART (UNCHANGED)
# -----------------------------
prod_df = merged.groupby("product")["price"].sum().reset_index()

fig2 = go.Figure(go.Bar(
    x=prod_df["product"],
    y=prod_df["price"]
))
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TREND (UNCHANGED)
# -----------------------------
trend = merged.set_index("time").resample("1min")["price"].sum().reset_index()

fig3 = go.Figure(go.Scatter(
    x=trend["time"],
    y=trend["price"],
    mode="lines+markers"
))
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TABLE (UNCHANGED)
# -----------------------------
st.dataframe(merged.sort_values("time", ascending=False).head(20), use_container_width=True)
