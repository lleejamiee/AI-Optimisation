import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAI
from gradio_client import Client
from prompts import tts_prompt_v2

# LLM
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
llm = client

# Prompt template(s)
tts_template = PromptTemplate.from_template(
    tts_prompt_v2)  # Prompt template, generating a script from the updated material

script_chain = (
        {"guide": RunnablePassthrough()}
        | tts_template
        | llm
        | StrOutputParser()
)

# Streamlit framework
st.set_page_config(page_title="Video", layout="wide")
st.header("Generate a Video")

# if the material has been input:
file = st.file_uploader("Upload", type="txt")

if file is not None:
    content = file.read().decode("utf-8")

    if content:
        tts_script = script_chain.invoke({"guide": content})
        st.write(tts_script)

    # TTS model
    client = Client("innoai/Edge-TTS-Text-to-Speech")
    result = client.predict(
        text=tts_script,
        voice="en-US-AvaNeural - en-US (Female)",
        rate=0,
        pitch=0,
        api_name="/predict"
    )
    print(result)
