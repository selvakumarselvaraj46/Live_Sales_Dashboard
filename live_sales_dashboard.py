import random
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Enterprise Revenue Command Center",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Enterprise Revenue Command Center")

st_autorefresh(interval=5000, key="refresh")

# -----------------------------
# PRODUCT DATABASE
# -----------------------------
PRODUCT_DB = {
"Mobile":{
"Apple":["iPhone 13","iPhone 14","iPhone 15","iPhone 15 Pro"],
"Samsung":["S23","S24","A54","M34"],
"OnePlus":["11R","12","Nord CE3"],
"Xiaomi":["Redmi Note 13","Mi 13","Poco F5"],
"Realme":["Narzo 60","GT Neo","Realme 11"],
"Oppo":["F21","Reno 10","A78"],
"Vivo":["V27","Y100","X90"],
"Google":["Pixel 7","Pixel 8"],
"Motorola":["Edge 40","G84","G54"],
"Nothing":["Phone 1","Phone 2"]
},
"Laptop":{
"Apple":["Macbook M1","Macbook M2"],
"Dell":["Inspiron","XPS","G15"],
"HP":["Victus","Omen","Pavilion"],
"Lenovo":["Legion","Thinkpad","IdeaPad"],
"Asus":["ROG","TUF","Vivobook"]
},
"Accessories":{
"Boat":["Earbuds","Headphones"],
"Noise":["Smartwatch","Earbuds"],
"Sony":["Headphones","Speaker"],
"JBL":["Speaker","Earbuds"],
"Firebolt":["Smartwatch"]
}
}

CITIES = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi","Pune","Kolkata","Ahmedabad"]
WEATHER_TYPES = ["Rain", "Heat", "Normal"]

PRICE_RANGE = {
"Mobile":[12000,90000],
"Laptop":[40000,150000],
"Accessories":[1000,15000]
}

# -----------------------------
# WEATHER SIMULATION
# -----------------------------
def get_weather():
    return {city: random.choice(WEATHER_TYPES) for city in CITIES}

# -----------------------------
# DATA GENERATION
# -----------------------------
def generate_data():
    rows=[]
    start=datetime(2023,1,1)

    while start < datetime.now():
        cat=random.choice(list(PRODUCT_DB.keys()))
        brand=random.choice(list(PRODUCT_DB[cat].keys()))
        model=random.choice(PRODUCT_DB[cat][brand])
        price=random.randint(*PRICE_RANGE[cat])
        city=random.choice(CITIES)

        rows.append([start,cat,brand,model,price,city])
        start+=timedelta(hours=random.randint(3,12))

    return pd.DataFrame(rows,columns=["timestamp","category","brand","model","price","city"])

# -----------------------------
# SESSION STATE
# -----------------------------
if "sales" not in st.session_state:
    st.session_state.sales=generate_data()

if "weather" not in st.session_state:
    st.session_state.weather = get_weather()

# -----------------------------
# LIVE SALES
# -----------------------------
def live_sale():
    cat=random.choice(list(PRODUCT_DB.keys()))
    brand=random.choice(list(PRODUCT_DB[cat].keys()))
    model=random.choice(PRODUCT_DB[cat][brand])
    price=random.randint(*PRICE_RANGE[cat])
    city=random.choice(CITIES)

    return {
        "timestamp":datetime.now(),
        "category":cat,
        "brand":brand,
        "model":model,
        "price":price,
        "city":city
    }

st.session_state.sales = pd.concat(
    [st.session_state.sales, pd.DataFrame([live_sale()])],
    ignore_index=True
)

df = st.session_state.sales.copy()

# -----------------------------
# DATE FIX
# -----------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["year"] = df["timestamp"].dt.year.astype(int)
df["month"] = df["timestamp"].dt.strftime("%b")

# Attach weather
df["weather"] = df["city"].map(st.session_state.weather)

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.title("Filters")

year=st.sidebar.multiselect("Year",sorted(df.year.unique()),default=sorted(df.year.unique()))
category=st.sidebar.multiselect("Category",df.category.unique(),default=df.category.unique())

brand=st.sidebar.multiselect(
    "Brand",
    df[df["category"].isin(category)]["brand"].unique(),
    default=df[df["category"].isin(category)]["brand"].unique()
)

model=st.sidebar.multiselect(
    "Product (Model)",
    df[(df["category"].isin(category)) & (df["brand"].isin(brand))]["model"].unique(),
    default=df[(df["category"].isin(category)) & (df["brand"].isin(brand))]["model"].unique()
)

city=st.sidebar.multiselect("City",df.city.unique(),default=df.city.unique())
weather=st.sidebar.multiselect("Weather",df.weather.unique(),default=df.weather.unique())

filtered=df[
    (df.year.isin(year))&
    (df.category.isin(category))&
    (df.brand.isin(brand))&
    (df.model.isin(model))&
    (df.city.isin(city))&
    (df.weather.isin(weather))
].copy()

# -----------------------------
# PROFIT
# -----------------------------
filtered["profit"]=filtered["price"]*random.uniform(0.08,0.22)

# -----------------------------
# KPI
# -----------------------------
col1,col2,col3,col4,col5=st.columns(5)

col1.metric("Revenue",f"₹{filtered.price.sum():,.0f}")
col2.metric("Orders",len(filtered))
col3.metric("Avg Order",f"₹{filtered.price.mean():,.0f}")
col4.metric("Profit",f"₹{filtered.profit.sum():,.0f}")

growth=filtered.groupby("year")["price"].sum().pct_change().mean()*100
col5.metric("YoY Growth",f"{growth:.1f}%")

# -----------------------------
# YEAR TREND (FIXED)
# -----------------------------
st.subheader("Year Trend")

year_df=(filtered.groupby("year")["price"].sum().reset_index().sort_values("year"))

# ✅ Convert to string to avoid decimal scale
year_df["year"] = year_df["year"].astype(str)

fig=px.bar(year_df,x="year",y="price",color="year",text_auto=True)

st.plotly_chart(fig,use_container_width=True)
