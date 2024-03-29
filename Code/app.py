import plotly.express as px
import streamlit as st
import analyst as al
import influx as db
import provider as pv
import pandas as pd
import datetime as dt

deployment = st.secrets["DEPLOYMENT"]

@st.cache_data
def make_impact_analysis(start, stop, deployment, source, currency = "USD", impact = "High"):
    analyst = al.Analyst(deployment = deployment, source = source)
    impact_frame = analyst.impact_analysis(start = pd.Timestamp(start), stop = pd.Timestamp(stop), currency = currency, impact = impact)
    return analyst.pretty_impact_analsysis(impact_frame)

@st.cache_data
def make_economic_calendar(start, stop, deployment, source, currency = "USD", impact = "High"):
    analyst = al.Analyst(deployment = deployment, source = source)
    return analyst.economic_calendar(start = pd.Timestamp(start), stop = pd.Timestamp(stop), currency = currency, impact = impact)

@st.cache_data
def make_regression_frame(start, stop, deployment, source, currency = "USD", impact = "High"):
    analyst = al.Analyst(deployment = deployment, source = source)
    raw_impact_frame = analyst.impact_analysis(start = pd.Timestamp(start), stop = pd.Timestamp(stop), currency = currency, impact = impact)
    clean_impact_frame = analyst.postprocess_impact_frame(raw_impact_frame)
    regression_frame = analyst.make_regression_frame(clean_impact_frame)
    return regression_frame[regression_frame["Count"] > 2]

title = "Impact Analysis"
description = "This is an work in progress project to analyze the impact of indicators of the economic calendar on currency-pair prices."

st.title(title)
st.write(description)

st.write("### Settings")
source_options = ["Dukascopy", "Axiory.com", "MetaTrader5", "MetaTrader4", "ForexTester.com", "TradeMade"]
selected_source = st.selectbox("Data Source:", source_options)

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

st.write("Selected Data Source:", selected_source)
st.write("Selected Currency:", selected_currency)
st.write("Selected Impact:", selected_impact)

st.write("### Economic Calendar")
st.write("Shows the Economic Events for the selected Currency and Impact")
economic_calendar = make_economic_calendar(start = start_date, stop = end_date, deployment = deployment, source = selected_source, currency = selected_currency, impact = selected_impact)
st.write(economic_calendar)

st.write("### Impact Analysis")
st.write("Calculates the Deviation between the Estimate and Actual Values for the Economic Events and the Impact on the Currency-Pair-Prices.")
impact_frame = make_impact_analysis(start = start_date, stop = end_date, deployment = deployment, source = selected_source, currency = selected_currency, impact = selected_impact)
st.write(impact_frame)

st.write("### Regression Analysis")
st.write("CoD - Coefficient of Determination")
st.write("Calculates the CoD for the Deviation and Impacts")
regression_frame = make_regression_frame(start = start_date, stop = end_date, deployment = deployment, source = selected_source, currency = selected_currency, impact = selected_impact)
st.write(regression_frame)

@st.cache_data
def make_heatmap(regression_frame):
    clean_regression_frame = regression_frame.drop(columns=["Count"])
    if clean_regression_frame.empty:
        return "Not enough Data for Heatmap"
    return px.imshow(clean_regression_frame, labels=dict(color="CoD"), aspect="auto", color_continuous_scale="rdylgn") 

st.write("### Heatmap for Regression Analysis")
figure = make_heatmap(regression_frame)
st.write(figure)