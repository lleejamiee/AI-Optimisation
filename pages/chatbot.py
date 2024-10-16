import streamlit as st

from utilities.chat import run_chatbot


def main():
    st.set_page_config(page_title="Chat", layout="wide")

    st.title("AI Chatbot")
    with st.expander("How to Use the Chatbot"):
        st.markdown("""
        1. Upload relevant documents for context
        2. Type your question or request about the contents of your document
        3. Review the AI's response
        4. Ask follow-up questions as needed
        """)


    run_chatbot()

if __name__ == "__main__":
    main()
