import streamlit as st
from groq import Groq
from utilities.chat_rag import ChatRAG
from utilities.prompts import chatbot_system
import os
from dotenv import load_dotenv

load_dotenv()


def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


def rag_response(prompt):
    response = st.session_state['rag'].rag_query(prompt)

    return response


def clear_chat_history():
    st.session_state.messages = []


def run_chatbot():
    if 'client' not in st.session_state:
        st.session_state.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    if 'rag' not in st.session_state:
        st.session_state.rag = ChatRAG()

    # Upload file
    with st.container(border=True):
        st.subheader("Upload Training Material")
        outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["docx", "pdf"])

    if st.button("Upload"):
        if outdated_guide_file is None:
            st.error("Please upload a file")
        else:
            clear_chat_history()
            st.session_state['rag'].create_rag_retriever(outdated_guide_file)

    # Set a default model
    if "groq_model" not in st.session_state:
        st.session_state["groq_model"] = "llama-3.2-90b-text-preview"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve context with prompt
        rag_prompt = rag_response(prompt)

        # Send user message
        with st.chat_message("assistant"):
            stream = st.session_state.client.chat.completions.create(
                model=st.session_state["groq_model"],
                messages=[
                    {"role": "system", "content": chatbot_system},
                    *st.session_state.messages,
                    {"role": "user", "content": rag_prompt}  # Include RAG context here
                ],
                temperature=0,
                stream=True,
            )

            response = st.write_stream(parse_groq_stream(stream))
        st.session_state.messages.append({"role": "assistant", "content": response})
