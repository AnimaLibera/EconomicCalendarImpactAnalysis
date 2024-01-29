import streamlit as st
import os

st.write("Impact Analysis!")
st.write("Secret Message:", os.environ['MESSAGE'], "via OS")
st.write("Secret Message:", st.secrets['MESSAGE'], "via Streamlit")