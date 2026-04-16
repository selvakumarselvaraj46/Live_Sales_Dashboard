import random
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise Revenue Intelligence 2020-2026", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: #0b0f19;
    color: #e6e6e6;
}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=5000, key="live")

# -----------------------------
# PRODUCTS (ENTERPRISE LEVEL)
# -----------------------------
PRODUCTS = {
    "MacBook Pro": 180000,
    "iPhone 15 Pro": 130000,
    "Samsung S24": 110000,
    "Dell XPS": 150000,
    "LG OLED TV": 90000,
    "Sony Headphones": 35000,
    "HP Laptop": 75000,
    "Lenovo ThinkPad": 140000,
    "AC 1.5T": 50000,
    "Washing Machine": 45000,
    "Canon DSLR": 80000,
    "Bluetooth Speaker": 8000
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
# WEATHER
# -----------------------------
@st.cache_data(ttl=600)
def get_weather(city):
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

# -----------------------------
# HISTORICAL DATA (2020–2025)
# -----------------------------
@st.cache_data
def generate_history():
    data = []
    for year in range(2020, 2026):
        for month in range(1, 13):
            for _ in range(60):  # monthly transactions
                product = random.choice(list(PRODUCTS.keys()))
                data.append({
                    "date": datetime(year, month, random.randint(1, 28)),
                    "year": year,
                    "month": month,
                    "product": product,
                    "city": random.choice(CITIES),
                    "price": PRODUCTS[product] + random.randint(-5000, 8000)
                })
    return pd.DataFrame(data)

hist_df = generate_history()

# -----------------------------
# LIVE DATA (2026 STREAM)
# -----------------------------
if "live_df" not in st.session_state:
    st.session_state.live_df = pd.DataFrame(columns=["date", "year", "product", "city", "price"])

def add_live():
    product = random.choice(list(PRODUCTS.keys()))
    st.session_state.live_df.loc[len(st.session_state.live_df)] = {
        "date": datetime.now(),
        "year": 2026,
        "product": product,
        "city": random.choice(CITIES),
        "price": PRODUCTS[product] + random.randint(-3000, 6000)
    }

add_live()

live_df = st.session_state.live_df

# -----------------------------
# COMBINED DATASET
# -----------------------------
df = pd.concat([hist_df, live_df], ignore_index=True)

df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

weather = pd.DataFrame([get_weather(c) for c in CITIES])

# -----------------------------
# FILTERS
# -----------------------------
st.title("📊 Enterprise Revenue Intelligence (2020 → Live 2026)")

st.sidebar.header("🎛️ Filters")

year_f = st.sidebar.multiselect("Year", sorted(df["year"].unique()), default=sorted(df["year"].unique()))
city_f = st.sidebar.multiselect("City", CITIES, default=CITIES)
product_f = st.sidebar.multiselect("Product", list(PRODUCTS.keys()), default=list(PRODUCTS.keys()))
weather_f = st.sidebar.multiselect("Weather", ["Heat", "Rain", "Normal"], default=["Heat","Rain","Normal"])

df = df[
    (df["year"].isin(year_f)) &
    (df["city"].isin(city_f)) &
    (df["product"].isin(product_f))
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
col4.metric("📅 Years Active", merged["year"].nunique())

st.markdown("---")

# -----------------------------
# 1. YEAR TREND (IMPORTANT)
# -----------------------------
st.subheader("📈 Year-wise Revenue Growth (2020–2026)")

year_df = merged.groupby("year", as_index=False)["price"].sum()

fig1 = px.line(year_df, x="year", y="price", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 2. CITY PERFORMANCE
# -----------------------------
st.subheader("🏙️ City Performance")

city_df = merged.groupby("city", as_index=False)["price"].sum().sort_values("price", ascending=False)

fig2 = px.bar(city_df, x="city", y="price", color="price", text="price")
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 3. PRODUCT PERFORMANCE
# -----------------------------
st.subheader("📦 Product Intelligence Matrix")

prod_df = merged.groupby("product", as_index=False)["price"].sum().sort_values("price", ascending=False)

fig3 = px.bar(prod_df, x="product", y="price", color="price")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 4. HEATMAP (ENTERPRISE INSIGHT)
# -----------------------------
st.subheader("🔥 Year vs Product Heatmap")

heat = merged.pivot_table(values="price", index="product", columns="year", aggfunc="sum", fill_value=0)

fig4 = px.imshow(heat, text_auto=True, aspect="auto")
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# 5. WEATHER IMPACT
# -----------------------------
st.subheader("🌦️ Weather Intelligence Layer")

wdf = merged.groupby("impact", as_index=False)["price"].sum()

fig5 = px.pie(wdf, names="impact", values="price", hole=0.55)
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# LIVE TABLE
# -----------------------------
st.subheader("🛰️ Live Enterprise Feed")

st.dataframe(
    merged.sort_values("date", ascending=False).head(20),
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚡ Enterprise System: Historical 2020–2026 + Live Stream + AI-ready structure")
