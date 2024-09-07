import os
import json
import nest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser

load_dotenv()

class MultiAgentRAG:
    Settings.llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_OPENAI_API_KEY"), temperature=0.4)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def save_uploaded_file(file):
        save_folder = Path('uploaded_files/')
        save_folder.mkdir(parents=True, exist_ok=True)
        save_path = save_folder / file.name
        with open(save_path, mode='wb') as w:
            w.write(file.getvalue())

        return save_path

    def load_document(file_path):
        document = SimpleDirectoryReader(input_files=[file_path]).load_data()
        splitter = SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95,
                                              embed_model=Settings.embed_model)
        nodes = splitter.get_nodes_from_documents(document)
        return nodes

    def load_webpage(url):
        document = SimpleWebPageReader(html_to_text=True).load_data([url])
        splitter = SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95,
                                              embed_model=Settings.embed_model)
        nodes = splitter.get_nodes_from_documents(document)
        return nodes

    def build_query_engine(outdated_node, reference_node):
        outdated_index = VectorStoreIndex(outdated_node)
        reference_index = VectorStoreIndex(reference_node)

        outdated_engine = outdated_index.as_query_engine()
        reference_engine = reference_index.as_query_engine()

        query_engine_tools = [
            QueryEngineTool(
                query_engine=outdated_engine,
                metadata=ToolMetadata(
                    name="Outdated Guide",
                    description="Contains the material from an Outdated User Guide",
                ),
            ),
            QueryEngineTool(
                query_engine=reference_engine,
                metadata=ToolMetadata(
                    name="Reference Guide",
                    description="Contains the material for updating the Outdated User Guide",
                ),
            ),
        ]

        s_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools)

        return s_engine

    def get_response_from_rag(s_engine, query):
        nest_asyncio.apply()
        response = s_engine.query(query)

        print(response)

        json_response = json.loads(str(response))
        change_dictionary = {}
        for change in json_response["Changes"]:
            outdated_step = change["Outdated Step"]
            updated_step = change["Updated Step"]
            change_dictionary[outdated_step] = updated_step

        return change_dictionary

    def update_document(updated_text, change_dictionary):
        for key, value in change_dictionary.items():
            if (value == "Delete"):
                updated_text = updated_text.replace(key, "")
            else:
                updated_text.replace(key, value)

        return updated_text
