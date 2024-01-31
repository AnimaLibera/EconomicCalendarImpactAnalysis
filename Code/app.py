import streamlit as st
import os
import analyst as al
import pandas as pd

title = "Impact Analysis"
description = "This is an work in progress project to analyze the impact of indicators of the economic calendar on currency-pair prices."

st.title(title)
st.write(description)

analyst = al.Analyst(deployment = "streamlit")

@st.cache_data
def make_impact_analysis(_analyst):
    start = pd.Timestamp("2023-12-15T00:00")
    stop = pd.Timestamp("2024-01-01T00:00")
    return analyst.new_impact_analysis(start, stop)

data_load_state = st.text('Loading data...')
data = make_impact_analysis(_analyst = analyst)
data_load_state.text('Loading data...done!')
st.write(data)