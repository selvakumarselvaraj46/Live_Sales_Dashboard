import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import requests
import plotly.express as px
from datetime import datetime
import sqlite3
from passlib.hash import pbkdf2_sha256
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Enterprise Command Center",
    layout="wide",
    page_icon="🚀"
)

# -----------------------------
# DATABASE
# -----------------------------

conn = sqlite3.connect("command_center.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    time TEXT,
    product TEXT,
    price INTEGER,
    city TEXT,
    weather TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS hospital(
    time TEXT,
    patientid INTEGER,
    triage INTEGER,
    wait INTEGER,
    department TEXT
)
""")

conn.commit()

# -----------------------------
# DEFAULT USERS
# -----------------------------

def create_default_users():
    users = cursor.execute("SELECT * FROM users").fetchall()
    if len(users) == 0:
        cursor.execute(
            "INSERT INTO users VALUES (?,?,?)",
            ("admin", pbkdf2_sha256.hash("admin123"), "Admin")
        )
        cursor.execute(
            "INSERT INTO users VALUES (?,?,?)",
            ("manager", pbkdf2_sha256.hash("manager123"), "Manager")
        )
        cursor.execute(
            "INSERT INTO users VALUES (?,?,?)",
            ("doctor", pbkdf2_sha256.hash("doctor123"), "Doctor")
        )
        conn.commit()

create_default_users()

# -----------------------------
# LOGIN
# -----------------------------

if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "user" not in st.session_state:
    st.session_state.user = ""

if not st.session_state.login:
    st.title("🔐 Enterprise Command Center Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and pbkdf2_sha256.verify(password, user[1]):
            st.session_state.login = True
            st.session_state.role = user[2]
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Invalid Login")

    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("Command Center")
st.sidebar.write(f"User: {st.session_state.user}")
st.sidebar.write(f"Role: {st.session_state.role}")

dashboard = st.sidebar.selectbox(
    "Select Dashboard",
    ["Live Revenue", "Hospital ER"]
)

refresh = st.sidebar.slider("Refresh Seconds", 5, 60, 10)

# Auto-refresh using streamlit-autorefresh (non-blocking)
st_autorefresh(interval=refresh * 1000, key="autorefresh")

# -----------------------------
# WEATHER API
# -----------------------------

OPENWEATHER_API_KEY = "YOUR_API_KEY"  # Replace with your actual key

def get_weather(city):
    if OPENWEATHER_API_KEY == "YOUR_API_KEY":
        return random.choice(["Clear", "Rain", "Clouds", "Heat"])
    try:
        api = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_API_KEY}"
        )
        r = requests.get(api, timeout=5).json()
        return r["weather"][0]["main"]
    except Exception:
        return "Clear"

# -----------------------------
# DATA GENERATORS
# -----------------------------

products = ["Laptop", "Mobile", "Tablet", "Camera", "Headphones", "Watch"]
cities   = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]
departments = ["Emergency", "Cardiology", "Orthopedic", "Neurology", "General"]

def generate_sale():
    city = random.choice(cities)
    return (
        datetime.now().isoformat(),   # FIX: store as string
        random.choice(products),
        random.randint(2000, 50000),
        city,
        get_weather(city)
    )

def generate_patient():
    return (
        datetime.now().isoformat(),   # FIX: store as string
        random.randint(1000, 9999),
        random.randint(1, 5),
        random.randint(5, 120),
        random.choice(departments)
    )

# -----------------------------
# SALES DASHBOARD
# -----------------------------

if dashboard == "Live Revenue":
    st.title("📈 Live Revenue Command Center")

    new_sale = generate_sale()
    cursor.execute("INSERT INTO sales VALUES (?,?,?,?,?)", new_sale)
    conn.commit()

    df = pd.read_sql("SELECT * FROM sales", conn)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"₹{df['price'].sum():,}")
    col2.metric("Orders", len(df))
    col3.metric("Avg Order", int(df["price"].mean()))
    col4.metric("Cities", df["city"].nunique())

    st.divider()

    col5, col6 = st.columns(2)

    with col5:
        fig = px.bar(df, x="city", y="price", title="City Revenue")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        fig = px.pie(df, names="product", title="Product Mix")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    if len(df) > 0:
        weather = df["weather"].value_counts().idxmax()
        if weather == "Rain":
            st.warning("☔ Rain is impacting sales")
        elif weather == "Heat":
            st.error("🌡️ Heat surge detected")

    st.subheader("Live Feed")
    st.dataframe(df.tail(15))

# -----------------------------
# HOSPITAL DASHBOARD
# -----------------------------

if dashboard == "Hospital ER":
    st.title("🏥 Emergency Command Center")

    new_patient = generate_patient()
    cursor.execute("INSERT INTO hospital VALUES (?,?,?,?,?)", new_patient)
    conn.commit()

    df = pd.read_sql("SELECT * FROM hospital", conn)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ER Load", len(df))
    col2.metric("Avg Wait", int(df["wait"].mean()))
    col3.metric("Critical", len(df[df["triage"] == 1]))
    col4.metric("Departments", df["department"].nunique())

    if len(df[df["triage"] == 1]) > 3:
        st.error("🚨 CRITICAL SURGE — Triage Level 1 patients exceeded threshold")

    st.divider()

    col5, col6 = st.columns(2)

    with col5:
        fig = px.bar(df, x="department", y="wait", title="Department Load")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        fig = px.histogram(df, x="triage", title="Triage Distribution")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Live Patient Feed")
    st.dataframe(df.tail(15))

# -----------------------------
# EXPORT
# -----------------------------

st.sidebar.divider()

if st.sidebar.button("Export Sales CSV"):
    df_sales = pd.read_sql("SELECT * FROM sales", conn)
    csv = df_sales.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="⬇️ Download Sales CSV",
        data=csv,
        file_name="sales_export.csv",
        mime="text/csv"
    )

if st.sidebar.button("Export Hospital CSV"):
    df_hosp = pd.read_sql("SELECT * FROM hospital", conn)
    csv = df_hosp.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="⬇️ Download Hospital CSV",
        data=csv,
        file_name="hospital_export.csv",
        mime="text/csv"
    )

# -----------------------------
# LOGOUT
# -----------------------------

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.session_state.user = ""
    st.session_state.role = ""
    st.rerun()