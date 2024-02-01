import streamlit as st
import analyst as al
import influx as db
import provider as pv
import pandas as pd


title = "Impact Analysis"
description = "This is an work in progress project to analyze the impact of indicators of the economic calendar on currency-pair prices."

st.title(title)
st.write(description)

analyst = al.Analyst(deployment = "linode")

@st.cache_data
def make_impact_analysis(_analyst):
    start = pd.Timestamp("2023-12-15T00:00")
    stop = pd.Timestamp("2024-01-01T00:00")
    return _analyst.new_impact_analysis(start, stop)

st.write("Impact Analysis")
impact_frame = make_impact_analysis(_analyst = analyst)
st.write(impact_frame)

database = db.InfluxDatabase(deployment = "linode")

currency_options = ("EUR", "USD", "GBP", "CAD", "JPY", "CHF", "AUD", "NZD")
selected_currency = st.selectbox("Currency:", currency_options)

start = pd.Timestamp("2023-12-15T00:00")
stop = pd.Timestamp("2024-01-01T00:00")
raw_economic_calendar = database.query_events(start = start, stop = stop, currency = selected_currency)
st.write("Raw Economic Calendar")
st.write(raw_economic_calendar)
nice_economic_calendar = database.preprocess_query_dataframe(raw_economic_calendar)
st.write("Nice Economic Calendar")
st.write(nice_economic_calendar)

st.write("Fooder")

#2023.12.29	23:58:00 (GMT+2)
#date = pd.Timestamp("2023-12-29T21:58")
#provider = pv.Provider(deployment = "linode")
#price = provider.foreign_exchange_rate_minute_close(date, "EURUSD")
#st.write(price)