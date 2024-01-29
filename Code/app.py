import streamlit as st
import os

st.write("Impact Analysis!")
#str.write("Secret Message:", os.environ['MESSAGE'], "via OS")
str.write("Secret Message:", st.secrets['MESSAGE'], "via Streamlit")