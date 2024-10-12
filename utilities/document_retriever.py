import os
from pathlib import Path
import re
from typing import List, Dict
from docx import Document
from llama_index.core import Settings, VectorStoreIndex, Document as LlamaDocument
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_parse import LlamaParse
from llama_index.core.tools import RetrieverTool
from llama_index.core.retrievers import VectorIndexRetriever, RouterRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.node_parser import SentenceSplitter
import pdf2docx
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
        saved_file = self._save_uploaded_file(file_path)
        extension = saved_file.suffix.lower()

        if extension == ".pdf":
            converted = self._convert_to_docx(saved_file)
            document = Document(converted)
        else:
            document = Document(saved_file)
        doc_text = "\n".join([para.text for para in document.paragraphs])

        return self._split_into_sections(doc_text)

    def _convert_to_docx(self, pdf_file):
        docx_file = pdf_file.with_suffix(".docx")
        pdf2docx.parse(str(pdf_file), str(docx_file))

        return docx_file

    def _split_into_sections(self, doc_text):
        sections = []

        pattern = re.compile(r'''
            ^
            (?P<Section>\d+(?:\.\d+)*)\s+
            (?P<Title>.+?)
            \n
            (?P<Content>(?:(?!^\d+(?:\.\d+)*\s+).+\n?)+)
        ''', re.MULTILINE | re.VERBOSE)

        for match in pattern.finditer(doc_text):
            sections.append({
                "title": f"{match.group('Section')} {match.group('Title')}",
                "content": match.group('Content').strip()
            })

        return sections

    def _create_documents(self, sections):
        documents = []
        for section in sections:
            text = f"{section['title']}\n\n{section['content']}"
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

    def rag_retrieval(self, outdated, reference, additional_reference):
        retrieved = []

        retriever = self._rag_components(outdated)
        processed = self._process_reference(reference)

        # Retrieve sections of the document using content from reference material file
        for ref in processed:
            result = retriever.retrieve(ref)
            retrieved.append(result)

        # Retrieve sections of the document using additional reference entries
        for ref in additional_reference:
            result = retriever.retrieve(ref)
            retrieved.append(result)

        return retrieved
