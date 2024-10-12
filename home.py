import streamlit as st

st.set_page_config(page_title="Home")
st.header("Select an option")

st.page_link("pages/document.py", label="Document")
st.page_link("pages/slide.py", label="Slide")
st.page_link("pages/video.py", label="Video")
st.page_link("pages/chatbot.py", label="Chat")