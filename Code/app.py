import streamlit as st
import analyst as al
import influx as db
import provider as pv
import pandas as pd

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
    return _analyst.new_impact_analysis(start, stop)

@st.cache_data
def make_economic_calendar(_database, currency = "USD", impact = "High"):
    start = pd.Timestamp("2023-12-15T00:00")
    stop = pd.Timestamp("2024-01-01T00:00")
    raw_economic_calendar = _database.query_events(start = start, stop = stop, currency = currency, impact = impact)
    nice_economic_calendar = _database.preprocess_query_dataframe(raw_economic_calendar)
    return nice_economic_calendar

st.write("### Impact Analysis")
impact_frame = make_impact_analysis(_analyst = analyst)
st.write(impact_frame)

st.write("### Economic Calendar")
currency_options = ("USD", "EUR", "GBP", "CAD", "JPY", "CHF", "AUD", "NZD")
selected_currency = st.selectbox("Currency:", currency_options)
impact_options = ("High", "Medium", "Low")
selected_impact = st.selectbox("Impact:", impact_options)
st.write("Selected Currency:", selected_currency)
st.write("Selected Impact:", selected_impact)
economic_calendar = make_economic_calendar(_database = database, currency = selected_currency, impact = selected_impact)
st.write(economic_calendar)

st.write("Fooder")