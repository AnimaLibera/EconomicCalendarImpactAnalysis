import streamlit as st
import os

st.write("Impact Analysis!")
str.write(f"Secret Message: {os.environ['MESSAGE']} via OS")
str.write(f"Secret Message: {st.secrets['MESSAGE']} via Streamlit")