import streamlit as st

st.set_page_config(page_title="Home")
st.header("Select an option")

st.page_link("pages/updating_app.py", label="Update")
st.page_link("pages/creating_app.py", label="Create")