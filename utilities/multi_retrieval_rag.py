import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_parse import LlamaParse
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.core.retrievers import RecursiveRetriever
from haystack import Document
from haystack.components.preprocessors import DocumentSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
from llama_index.core.postprocessor import LLMRerank

load_dotenv()


class MultiRetrievalRag:
    Settings.llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0.4)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def load_outdated(file_path):
        document = LlamaParse(num_workers=8, split_by_page=0, result_type="text").load_data(file_path)
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=90)
        chunks = splitter.get_nodes_from_documents(document)

        return chunks

    def load_reference(file_path):
        document = LlamaParse(split_by_page=0, result_type="text").load_data(file_path)
        splitter = DocumentSplitter(split_by="passage", split_length=1, split_overlap=0)
        chunks = splitter.run(documents=[Document(content=document[0].text)])

        return chunks

    def split_into_paragraphs(text):
        paragraphs = text.split('\n\n')
        return [para.strip() for para in paragraphs if para.strip()]

    def create_subnodes(chunks):
        all_subnodes = []
        subnode_to_basenode_map = {}

        for base_node in chunks:
            paragrpahs = MultiRetrievalRag.split_into_paragraphs(base_node.text)

            for paragraph in paragrpahs:
                sub_node = TextNode(text=paragraph, metadata=base_node.metadata.copy())
                sub_node.metadata["base_node_id"] = base_node.node_id
                all_subnodes.append(sub_node)
                subnode_to_basenode_map[sub_node.node_id] = base_node

        return all_subnodes, subnode_to_basenode_map

    def create_vector_index(nodes):
        vector_index = VectorStoreIndex(nodes)

        return vector_index

    def create_queries(chunks):
        queries = []
        for chunk in chunks['documents']:
            queries.append(chunk.content)

        return queries

    def retrieve_subnodes(all_subnodes, query, vector_index, top_k=2):
        vector_retriever = vector_index.as_retriever(similarity_top_k=top_k)

        all_nodes_dict = {n.node_id: n for n in all_subnodes}

        retriever = RecursiveRetriever(
            "vector",
            retriever_dict={"vector": vector_retriever},
            node_dict=all_nodes_dict,
            verbose=True,
        )

        retrieved_nodes = retriever.retrieve(query)

        return retrieved_nodes

    def chunks_to_index(chunks):
        nodes = []
        for chunk in chunks:
            nodes.append(TextNode(text=chunk.get_content()))

        index = VectorStoreIndex(nodes)

        return index

    def get_retrieved_nodes(query_str, index, vector_top_k=10, reranker_top_n=3, with_reranker=False):
        query_bundle = QueryBundle(query_str)
        retriever=VectorIndexRetriever(index=index,similarity_top_k=vector_top_k)

        retrieved_nodes = retriever.retrieve(query_bundle)

        if with_reranker:
            reranker = LLMRerank(choice_batch_size=5,top_n=reranker_top_n)
            retrieved_nodes = reranker.postprocess_nodes(retrieved_nodes,query_bundle)

        return retrieved_nodes

    def create_pairs(reference):
        context_pairs = []
        i = 0
        for text_chunk in reference:
            result_nodes = MultiRetrievalRag.get_retrieved_nodes(text_chunk.content)
            result = (text_chunk, result_nodes[0])
            context_pairs.append(result)

            i += 1

        return context_pairs