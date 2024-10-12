import streamlit as st

from utilities.document_update import run_update_tab
from utilities.document_create import run_create_tab


def main():
    st.set_page_config(page_title="Chat", layout="wide")

    st.header("AI Chatbot")

if __name__ == "__main__":
    main()
