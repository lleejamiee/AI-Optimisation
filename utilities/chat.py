import streamlit as st
from groq import Groq
from utilities.chat_rag import ChatRAG
from utilities.prompts import chat_bot
import os
from dotenv import load_dotenv

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


def run_chatbot():
    # Set a default model
    if "groq_model" not in st.session_state:
        st.session_state["groq_model"] = "llama3-8b-8192"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send user message
        with st.chat_message("assistant"):
            stream = groq_client.chat.completions.create(
                model=st.session_state["groq_model"],
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                stream=True,
            )

            response = st.write_stream(parse_groq_stream(stream))
        st.session_state.messages.append({"role": "assistant", "content": response})
