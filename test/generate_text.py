from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack import Document
from haystack.components.converters.txt import TextFileToDocument
from haystack.utils import Secret
import os
from dotenv import load_dotenv
from utilities.prompts import *

load_dotenv()

# Convert .txt to document (not .docx)
converter = TextFileToDocument()
results = converter.run(sources=["reference.txt", "outdated.txt"])

# Add documents (only .txt atm)
documents = results["documents"]
docstore = InMemoryDocumentStore()
docstore.write_documents([Document(content=documents[0].content), Document(content=documents[1].content)])

# Prompt templates
text_template = text_template
slides_template = slides_template
script_template = script_template

# Queries
text_query = text_query
slides_query = slides_query
script_query = script_query

def create_llm(temp):
    return OpenAIGenerator(
        api_key=Secret.from_env_var("GROQ_OPENAI_API_KEY"),
        api_base_url="https://api.groq.com/openai/v1",
        model="llama3-8b-8192",
        generation_kwargs={"temperature": temp}  # TEMP 0.2 "n":2
    )

# Pipeline function for text, slides, TTS scripts
def inference_pipeline(query, template, docstore, temp=0.2):
    llm = create_llm(temp)
    pipe = Pipeline()
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=docstore))
    pipe.add_component("prompt_builder", PromptBuilder(template=template))
    pipe.add_component("llm", llm)
    pipe.connect("retriever", "prompt_builder.documents")
    pipe.connect("prompt_builder", "llm")

    res = pipe.run({"retriever": {"query": query},"prompt_builder": {"query": query}})

    # Returns the LLM generated response
    return res['llm']['replies'][0]

# Call inference_pipline function for text, slides, and script
generate_text = inference_pipeline(text_query, text_template, docstore)
documents = str(generate_text)
docstore.write_documents([Document(content=documents, meta={"name": "updated"})]) # Store the updated content as a document(not .docx) to the in memory doc store

generate_slides = inference_pipeline(slides_query, slides_template, docstore, temp=0.5)

generate_script = inference_pipeline(script_query, script_template, docstore, temp=0.6)

print(generate_text)
print(generate_slides)
print(generate_script)