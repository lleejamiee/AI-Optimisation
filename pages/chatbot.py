import streamlit as st

from utilities.chat import run_chatbot


def main():
    st.set_page_config(page_title="Chat", layout="wide")

    st.title("AI Chatbot")
    run_chatbot()

if __name__ == "__main__":
    main()
