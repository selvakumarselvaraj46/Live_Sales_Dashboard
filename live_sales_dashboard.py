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

CITIES = [
"Chennai","Bangalore","Hyderabad","Mumbai",
"Delhi","Pune","Kolkata","Ahmedabad"
]

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
# HISTORICAL DATA
# -----------------------------

def generate_data():
    rows=[]
    start=datetime(2023,1,1)

    while start < datetime.now():
        cat=random.choice(list(PRODUCT_DB.keys()))
        brand=random.choice(list(PRODUCT_DB[cat].keys()))
        model=random.choice(PRODUCT_DB[cat][brand])
        price=random.randint(
            PRICE_RANGE[cat][0],
            PRICE_RANGE[cat][1]
        )
        city=random.choice(CITIES)

        rows.append([
            start,cat,brand,model,price,city
        ])

        start+=timedelta(hours=random.randint(3,12))

    return pd.DataFrame(
        rows,
        columns=["timestamp","category","brand","model","price","city"]
    )

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
    price=random.randint(
        PRICE_RANGE[cat][0],
        PRICE_RANGE[cat][1]
    )
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
    [st.session_state.sales, pd.DataFrame([live_sale()])]
)

df = st.session_state.sales.copy()

# Attach weather
df["weather"] = df["city"].map(st.session_state.weather)

df["year"]=df.timestamp.dt.year
df["month"]=df.timestamp.dt.month_name()

# -----------------------------
# FILTERS
# -----------------------------

st.sidebar.title("Filters")

year=st.sidebar.multiselect(
    "Year",df.year.unique(),default=df.year.unique()
)

category=st.sidebar.multiselect(
    "Category",df.category.unique(),default=df.category.unique()
)

brand=st.sidebar.multiselect(
    "Brand",
    df[df["category"].isin(category)]["brand"].unique(),
    default=df[df["category"].isin(category)]["brand"].unique()
)

# ✅ NEW PRODUCT (MODEL) FILTER (DYNAMIC)
model=st.sidebar.multiselect(
    "Product (Model)",
    df[
        (df["category"].isin(category)) &
        (df["brand"].isin(brand))
    ]["model"].unique(),
    default=df[
        (df["category"].isin(category)) &
        (df["brand"].isin(brand))
    ]["model"].unique()
)

city=st.sidebar.multiselect(
    "City",df.city.unique(),default=df.city.unique()
)

weather=st.sidebar.multiselect(
    "Weather",
    df.weather.unique(),
    default=df.weather.unique()
)

filtered=df[
    (df.year.isin(year))&
    (df.category.isin(category))&
    (df.brand.isin(brand))&
    (df.model.isin(model))&   # ✅ applied here
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
# WEATHER IMPACT
# -----------------------------

st.subheader("🌦 Weather Impact on Sales")

weather_sales = filtered.groupby("weather")["price"].sum().reset_index()

fig = px.bar(weather_sales, x="weather", y="price")
st.plotly_chart(fig, use_container_width=True)

st.write("### Current Weather by City")

weather_df = pd.DataFrame(
    list(st.session_state.weather.items()),
    columns=["City","Weather"]
)

st.dataframe(weather_df)

# -----------------------------
# AI FORECAST
# -----------------------------

st.subheader("AI Revenue Forecast")

monthly=filtered.set_index("timestamp").resample("ME")["price"].sum()

forecast=monthly.tail(3).mean()

st.metric("Next Month Prediction",f"₹{forecast:,.0f}")

fig=px.line(monthly)
st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# YEAR TREND
# -----------------------------

st.subheader("Year Trend")

year_df=filtered.groupby("year")["price"].sum().reset_index()

fig=px.bar(year_df,x="year",y="price")
st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# CATEGORY
# -----------------------------

col1,col2=st.columns(2)

with col1:
    cat=filtered.groupby("category")["price"].sum().reset_index()
    fig=px.pie(cat,names="category",values="price")
    st.plotly_chart(fig,use_container_width=True)

with col2:
    brand_df=filtered.groupby("brand")["price"].sum().reset_index()
    fig=px.bar(brand_df,x="brand",y="price")
    st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# INVENTORY
# -----------------------------

if "inventory" not in st.session_state:
    data=[]
    for cat in PRODUCT_DB:
        for brand in PRODUCT_DB[cat]:
            for model_name in PRODUCT_DB[cat][brand]:
                data.append([
                    cat,brand,model_name,
                    random.randint(20,120)
                ])

    st.session_state.inventory=pd.DataFrame(
        data,
        columns=["category","brand","model","stock"]
    )

st.subheader("Inventory")
st.dataframe(st.session_state.inventory)

# -----------------------------
# ALERTS
# -----------------------------

st.subheader("Alerts")

low=st.session_state.inventory[
    st.session_state.inventory.stock<30
]

if not low.empty:
    st.warning("Low Inventory")

recent=filtered.tail(20)["price"].sum()

if recent>500000:
    st.success("Sales Spike Detected")

# -----------------------------
# MODEL LEADERBOARD
# -----------------------------

st.subheader("Top Models")

top=filtered.groupby("model")["price"].sum().reset_index()
top=top.sort_values("price",ascending=False).head(10)

st.dataframe(top)

# -----------------------------
# LIVE SALES
# -----------------------------

st.subheader("Live Sales")

live=filtered.sort_values(
    "timestamp",
    ascending=False
).head(20)

st.dataframe(live)
 i no need weather remove the weather in above code and give me full code in single block code
