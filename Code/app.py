import streamlit as st
import analyst as al
import influx as db
import provider as pv
import pandas as pd
import datetime as dt

title = "Impact Analysis"
description = "This is an work in progress project to analyze the impact of indicators of the economic calendar on currency-pair prices."

st.title(title)
st.write(description)

deployment = st.secrets["DEPLOYMENT"]
analyst = al.Analyst(deployment = deployment)
database = db.InfluxDatabase(deployment = deployment)

@st.cache_data
def make_impact_analysis(_analyst):
    start = pd.Timestamp("2023-12-15T00:00")
    stop = pd.Timestamp("2024-01-01T00:00")
    return _analyst.impact_analysis(start, stop)

@st.cache_data
def make_economic_calendar(_database, start, stop, currency = "USD", impact = "High"):
    #start = pd.Timestamp("2023-12-15T00:00")
    #stop = pd.Timestamp("2024-01-01T00:00")
    raw_economic_calendar = _database.query_events(start = pd.Timestamp(start), stop = pd.Timestamp(stop), currency = currency, impact = impact)
    nice_economic_calendar = _database.preprocess_query_dataframe(raw_economic_calendar)
    return nice_economic_calendar

st.write("### Impact Analysis")
impact_frame = make_impact_analysis(_analyst = analyst)
st.write(impact_frame)

st.write("### Economic Calendar")
min_date = dt.date(2023, 1, 1)
max_date = dt.date(2023, 12,31)
start_value = dt.date(2023, 12, 1)
start_date = st.date_input("Startdate", value = start_value, min_value = min_date, max_value = max_date)
end_date = st.date_input("Enddate", value = max_date, min_value = min_date, max_value = max_date)

if start_date > end_date:
    st.write("Warning: Startdate is after Enddate")

currency_options = ("USD", "EUR", "GBP", "CAD", "JPY", "CHF", "AUD", "NZD")
selected_currency = st.selectbox("Currency:", currency_options)

impact_options = ("High", "Medium", "Low")
selected_impact = st.selectbox("Impact:", impact_options)

st.write("Selected Currency:", selected_currency)
st.write("Selected Impact:", selected_impact)
economic_calendar = make_economic_calendar(_database = database, start = start_date, stop = end_date, currency = selected_currency, impact = selected_impact)
st.write(economic_calendar)

st.write("Fooder")