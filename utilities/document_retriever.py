import os
from pathlib import Path
import re
from docx import Document
from llama_index.core import Settings, VectorStoreIndex, Document as LlamaDocument
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_parse import LlamaParse
from llama_index.core.tools import RetrieverTool
from llama_index.core.retrievers import VectorIndexRetriever, RouterRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()


class DocumentRetriever:
    def __init__(self):
        Settings.llm = Groq(model="llama-3.2-90b-text-preview", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        os.getenv("LLAMA_CLOUD_API_KEY")
        os.getenv("GROQ_API_KEY")

    def _process_reference(self, file_path):
        reference_file = self._save_uploaded_file(file_path)
        reference = LlamaParse(num_workers=8, split_by_page=0, result_type="text").load_data(reference_file)
        reference_split = self._split_into_paragraphs(reference[0].text)
        return reference_split

    def _save_uploaded_file(self, file):
        save_folder = Path('uploaded_files/')
        save_folder.mkdir(parents=True, exist_ok=True)
        save_path = save_folder / file.name
        with open(save_path, mode='wb') as w:
            w.write(file.getvalue())
        return save_path

    def _split_into_paragraphs(self, text):
        paragraphs = text.split('\n\n')
        return [para.strip() for para in paragraphs if para.strip()]

    def _process_document(self, file_path):
        outdated_file = self._save_uploaded_file(file_path)
        document = Document(outdated_file)
        sections = self._split_into_sections(document)
        return sections

    def _split_into_sections(self, document):
        sections = []
        current_section = {"title": "", "content": []}
        for paragraph in document.paragraphs:
            if re.match(r'^\d+\.', paragraph.text.strip()):
                if current_section["title"]:
                    sections.append(current_section)
                current_section = {"title": paragraph.text.strip(), "content": []}
            else:
                current_section["content"].append(paragraph.text)
        if current_section["title"]:
            sections.append(current_section)
        return sections

    def _create_documents(self, sections):
        documents = []
        for section in sections:
            text = f"{section['title']}\n\n"
            if isinstance(section['content'], list):
                text += "\n".join(section['content'])
            else:
                text += str(section['content'])
            doc = LlamaDocument(text=text)
            documents.append(doc)
        return documents

    def _create_index(self, documents, vector_index=None):
        if vector_index is None:
            vector_index = VectorStoreIndex([])
        for doc in documents:
            vector_index.insert(doc)
        return vector_index

    def _create_retriever(self, documents, vector_index):
        parser = SentenceSplitter()
        nodes = parser.get_nodes_from_documents(documents)

        vector_retriever = VectorIndexRetriever(vector_index, similarity_top_k=6)
        bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=6)

        retriever_tools = [
            RetrieverTool.from_defaults(
                retriever=vector_retriever,
                description="Useful in most cases",
            ),
            RetrieverTool.from_defaults(
                retriever=bm25_retriever,
                description="Useful if searching about specific information",
            ),
        ]

        router_retriever = RouterRetriever.from_defaults(
            retriever_tools=retriever_tools,
            select_multi=True,
        )

        return router_retriever

    def _rag_components(self, file_path):
        sections = self._process_document(file_path)
        documents = self._create_documents(sections)
        vector_index = self._create_index(documents)
        retriever = self._create_retriever(documents, vector_index)
        return retriever

    def rag_retrieval(self, outdated, reference):
        retrieved = []

        retriever = self._rag_components(outdated)
        processed = self._process_reference(reference)
        for ref in processed:
            result = retriever.retrieve(ref)
            retrieved.append(result)
            # print(result[0].text)

        return retrieved
