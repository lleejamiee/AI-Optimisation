import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI
from gradio_client import Client

# Prompt templates (Create file later)
tts_prompt = """ 
Convert the following {guide} content into a clear, engaging, and conversational transcript designed for a 
person to read aloud in a training video. Ensure the language is simple and accessible, while maintaining the 
instructional integrity of the content. Add any necessary transitions, introductions, and summaries to make the 
material flow naturally. Avoid overly technical jargon and keep the tone friendly and authoritative.
"""

tts_template = PromptTemplate( # Prompt template, generating a script from the updated material
	input_variables=["guide"],
	template=tts_prompt
)

# LLM
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
llm = client
# llm = AzureOpenAI(
# 	api_key=AOAI_KEY,
# 	azure_endpoint=AOAI_ENDPOINT,
# 	model="hackathon-GPT-4",
# 	api_version="2024-05-01-preview",
# 	temperature=0.3
# )

script_chain = tts_template | llm | StrOutputParser()

# Streamlit framework
st.set_page_config(page_title="Video", layout="wide")
st.header("Generate a Video")

# if the material has been input:
file = st.file_uploader("Updated", type="txt")
content = file.read().decode("utf-8")

if content:
	# st.write(content)
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