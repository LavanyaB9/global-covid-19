# app.py
"""
Global COVID-19 Data Analysis and Visualization
- uses cached local pickle (super fast)
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(page_title="Global COVID-19 Data Analysis and Visualization", layout="wide")
st.title("🌍 Global COVID-19 Data Analysis and Visualization")

PICKLE_FILE = "covid.pkl"

# ------------------------------------------------------------------
# create small local dataset on first run (no download needed)
# ------------------------------------------------------------------
def create_local_data():
    data = {
        "date": pd.date_range("2020-01-01", periods=600),
        "location": ["India"]*200 + ["USA"]*200 + ["UK"]*200,
        "total_cases": np.random.randint(100, 100000, 600),
        "total_deaths": np.random.randint(1, 2000, 600)
    }
    df = pd.DataFrame(data)
    df.to_pickle(PICKLE_FILE)

# ------------------------------------------------------------------
# cached fast loading
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    if not os.path.exists(PICKLE_FILE):
        create_local_data()
    return pd.read_pickle(PICKLE_FILE)

df = load_data()


# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------
st.sidebar.header("Filters")
min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input("Date range", [min_date.date(), max_date.date()])
start_date, end_date = map(pd.to_datetime, date_range)

df_filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

top_n = st.sidebar.slider("Top N countries", 5, 30, 10)


# summary
latest = df_filtered.sort_values("date").groupby("location", as_index=False).last()

col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{len(df_filtered):,}")
col2.metric("Countries", latest["location"].nunique())
col3.metric("Date Range", f"{start_date.date()} → {end_date.date()}")


# ------------------------------------------------------------------
# Top N
# ------------------------------------------------------------------
st.subheader(f"Top {top_n} Countries by Total Cases")
top_countries = latest.sort_values("total_cases", ascending=False).head(top_n)
st.plotly_chart(px.bar(top_countries, x="location", y="total_cases"), use_container_width=True)


# ------------------------------------------------------------------
# country timeline
# ------------------------------------------------------------------
st.subheader("Country Timeline")
countries = sorted(df_filtered["location"].unique())
country = st.selectbox("Country", countries)

ts = df_filtered[df_filtered["location"] == country]

st.plotly_chart(px.line(ts, x="date", y=["total_cases", "total_deaths"]), use_container_width=True)


# ------------------------------------------------------------------
# bubble
# ------------------------------------------------------------------
st.subheader("Bubble — Cases vs Deaths (latest per country)")
bubble = latest[(latest["total_cases"] > 0) & (latest["total_deaths"] > 0)]
fig = px.scatter(
    bubble,
    x="total_cases",
    y="total_deaths",
    size="total_cases",
    hover_name="location",
    log_x=True,
    log_y=True,
)
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------------
# preview + download
# ------------------------------------------------------------------
st.subheader("Data Preview")
st.dataframe(df_filtered.head(50))

@st.cache_data
def to_csv_bytes(d):
    return d.to_csv(index=False).encode("utf-8")

st.download_button("Download Filtered CSV", to_csv_bytes(df_filtered), "covid_filtered.csv", "text/csv")
