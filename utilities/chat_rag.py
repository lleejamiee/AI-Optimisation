from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever

from pathlib import Path
import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

load_dotenv()


class ChatRAG:
    def __init__(self):
        self.retriever = None

        Settings.llm = Groq(model="llama-3.2-90b-text-preview", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        os.getenv("GROQ_API_KEY")

    # Process uploaded document and load its content
    def _process_document(self, file_path):
        saved_file = self._save_uploaded_file(file_path)
        document = SimpleDirectoryReader(input_files=[saved_file]).load_data()

        return document

    # Save uploaded file to a local directory
    def _save_uploaded_file(self, file):
        save_folder = Path('uploaded_files/')
        save_folder.mkdir(parents=True, exist_ok=True)
        save_path = save_folder / file.name
        with open(save_path, mode='wb') as w:
            w.write(file.getvalue())

        return save_path

    # Split document into chunks for indexing
    def _create_chunks(self, document):
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=128)
        chunks = splitter.get_nodes_from_documents(document)
        print(chunks)

        return chunks

    # Create a vector index and retriever from document chunks
    def _create_retriever(self, chunks):
        vector_index = VectorStoreIndex(chunks)
        vector_retriever = VectorIndexRetriever(vector_index)

        return vector_retriever

    # RAG pipeline
    def create_rag_retriever(self, file_path):
        document = self._process_document(file_path)
        chunks = self._create_chunks(document)
        self.retriever = self._create_retriever(chunks)

    def rag_query(self, chat_message):
        response = self.retriever.retrieve(chat_message)
        prompt = f"Query: {chat_message}\n\nContext: {response[0].text}"

        return prompt
