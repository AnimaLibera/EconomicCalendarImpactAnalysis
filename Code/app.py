import streamlit as st
import analyst as al
import influx as db
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

data_load_state = st.text('Loading data...')
#impact_frame = make_impact_analysis(_analyst = analyst)
data_load_state.text('Loading data...done!')
#st.write(impact_frame)
st.write("Fooder")

database = db.InfluxDatabase(deployment = "linode")
st.write(database)
start = pd.Timestamp("2023-12-15T00:00")
stop = pd.Timestamp("2024-01-01T00:00")
raw_economic_calendar = database.query_events(start = start, stop = stop)
st.write(raw_economic_calendar)