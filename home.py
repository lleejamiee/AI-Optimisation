import streamlit as st

st.set_page_config(page_title="Home")
st.header("Select an option")

st.page_link("pages/create.py", label="Create")
st.page_link("pages/update.py", label="Update")