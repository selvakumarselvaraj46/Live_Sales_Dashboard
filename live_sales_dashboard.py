import streamlit as st
import pandas as pd
import numpy as np
import random
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

st.sidebar.title("🚀 Command Center")

st.sidebar.success(f"User : {st.session_state.user}")
st.sidebar.info(f"Role : {st.session_state.role}")

dashboard = st.sidebar.selectbox(
    "Select Dashboard",
    ["Live Revenue", "Hospital ER"]
)

refresh = st.sidebar.slider("Refresh Seconds", 5, 60, 10)

st_autorefresh(interval=refresh * 1000, key="refresh")

# -----------------------------
# WEATHER
# -----------------------------

def get_weather(city):

    try:
        # fallback weather simulation
        return random.choice(
            ["Clear","Rain","Clouds","Heat"]
        )

    except:
        return "Clear"

# -----------------------------
# DATA GENERATORS
# -----------------------------

products = [
    "Laptop","Mobile","Tablet",
    "Camera","Headphones","Watch"
]

cities = [
    "Chennai","Mumbai",
    "Delhi","Bangalore",
    "Hyderabad"
]

departments = [
    "Emergency",
    "Cardiology",
    "Orthopedic",
    "Neurology",
    "General"
]

def generate_sale():

    city = random.choice(cities)

    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.randint(2000,50000),
        city,
        get_weather(city)
    )


def generate_patient():

    return (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.randint(1000,9999),
        random.randint(1,5),
        random.randint(5,120),
        random.choice(departments)
    )

# -----------------------------
# SALES DASHBOARD
# -----------------------------

if dashboard == "Live Revenue":

    st.title("📈 Live Revenue Command Center")

    new_sale = generate_sale()

    cursor.execute(
        "INSERT INTO sales VALUES (?,?,?,?,?)",
        new_sale
    )

    conn.commit()

    df = pd.read_sql("SELECT * FROM sales", conn)

    if len(df) > 0:

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Total Revenue", f"₹{df['price'].sum():,}")
        col2.metric("Orders", len(df))
        col3.metric("Avg Order", int(df["price"].mean()))
        col4.metric("Cities", df["city"].nunique())

        st.divider()

        col5,col6 = st.columns(2)

        with col5:
            fig = px.bar(
                df,
                x="city",
                y="price",
                title="City Revenue",
                color="city"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col6:
            fig = px.pie(
                df,
                names="product",
                title="Product Mix"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        weather = df["weather"].value_counts().idxmax()

        if weather == "Rain":
            st.warning("🌧 Rain Impact Sales")

        if weather == "Heat":
            st.error("🔥 Heat Surge")

        st.subheader("Live Feed")
        st.dataframe(df.tail(15), use_container_width=True)

# -----------------------------
# HOSPITAL DASHBOARD
# -----------------------------

if dashboard == "Hospital ER":

    st.title("🏥 Emergency Command Center")

    new_patient = generate_patient()

    cursor.execute(
        "INSERT INTO hospital VALUES (?,?,?,?,?)",
        new_patient
    )

    conn.commit()

    df = pd.read_sql("SELECT * FROM hospital", conn)

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("ER Load", len(df))
    col2.metric("Avg Wait", int(df["wait"].mean()))
    col3.metric("Critical", len(df[df["triage"]==1]))
    col4.metric("Departments", df["department"].nunique())

    if len(df[df["triage"]==1]) > 3:
        st.error("🚨 CRITICAL SURGE")

    st.divider()

    col5,col6 = st.columns(2)

    with col5:
        fig = px.bar(
            df,
            x="department",
            y="wait",
            color="department",
            title="Department Load"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        fig = px.histogram(
            df,
            x="triage",
            title="Triage Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Live Patient Feed")
    st.dataframe(df.tail(15), use_container_width=True)

# -----------------------------
# EXPORT
# -----------------------------

st.sidebar.divider()

if st.sidebar.button("Export Sales CSV"):
    df = pd.read_sql("SELECT * FROM sales", conn)
    df.to_csv("sales_export.csv", index=False)
    st.sidebar.success("Exported")

if st.sidebar.button("Export Hospital CSV"):
    df = pd.read_sql("SELECT * FROM hospital", conn)
    df.to_csv("hospital_export.csv", index=False)
    st.sidebar.success("Exported")

# -----------------------------
# LOGOUT
# -----------------------------

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()
