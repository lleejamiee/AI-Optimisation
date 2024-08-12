import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAI, AzureChatOpenAI
from gradio_client import Client
from prompts import *

load_dotenv()

# LLM
llm = AzureChatOpenAI(
    deployment_name=os.getenv("DEPLOYMENT_NAME"),
    openai_api_version="2024-06-01",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    temperature=0.7
)

# Prompt template(s)
user_prompt = tts_prompt_v5 # Updated prompt v4
full_prompt = f"{system_prompt_v2}\n\n{user_prompt}\n\n{{guide}}"

tts_template = PromptTemplate.from_template(full_prompt)

# Chains - only script_chain for now
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
        rate=1,
        pitch=4,
        api_name="/predict"
    )
    print(result)
