import streamlit as st

from utilities.document_processor import DocumentProcessor
from utilities.multi_agent_rag import MultiAgentRAG
from utilities.multi_retrieval_rag import MultiRetrievalRag

# Prompt for LLM
prompt = """
You are a technical writer tasked with updating an outdated user guide for a product/service. 
Your task is to update an outdated user guide by incorporating relevant information from the provided reference material.
Only generate the content that is to be used in this updated user guide.
Do not provide explanations or notes.

The user will input one text document
Document 1: Outdated User Guide
Document 2: Reference Material
"""


def main():
    st.set_page_config(page_title="Update a Document", layout="wide")

    # Set app header
    st.header("Update a Document")

    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["txt", "pdf", "docx", "pptx"])
    reference_material_file = st.file_uploader("Choose the reference material document",
                                               type=["txt", "pdf", "docx", "pptx"])
    webpage_link = st.text_input("Input webpage link")

    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = None

    if st.button("Generate Updated Guide"):
        if outdated_guide_file is not None:
            outdated_path = MultiAgentRAG.save_uploaded_file(outdated_guide_file)
            st.session_state.outdated_chunks = MultiRetrievalRag.load_outdated(outdated_path)

            if reference_material_file or webpage_link is not None:
                if reference_material_file:
                    reference_path = MultiAgentRAG.save_uploaded_file(reference_material_file)
                    st.session_state.reference_chunks = MultiRetrievalRag.load_reference(reference_path)

                if webpage_link:
                    st.session_state.reference_node = MultiAgentRAG.load_webpage(webpage_link)
            else:
                st.error("Please upload either reference material or webpage link.")

        else:
            st.error("Please upload outdated material.")

    if 'outdated_chunks' and 'reference_chunks' in st.session_state:
        subnodes, nodes_map = MultiRetrievalRag.create_subnodes(st.session_state.outdated_chunks)
        queries = MultiRetrievalRag.create_queries(st.session_state.reference_chunks)
        vector_index = MultiRetrievalRag.create_vector_index(subnodes)

        for query in queries:
            retrieved_subnodes = MultiRetrievalRag.retrieve_subnodes(subnodes, query, vector_index)

            for subnode in retrieved_subnodes:
                print(subnode.text)



    # if st.session_state.generated_text:
    #     st.subheader("Updated User Guide Content")
    #
    #     if "edit_mode" not in st.session_state:
    #         st.session_state.edit_mode = False
    #
    #     outdated_guide_compared, updated_guide_compared = DocumentProcessor.compare_texts(
    #         st.session_state.outdated_guide_text, st.session_state.generated_text)
    #
    #     if st.session_state.edit_mode:
    #         DocumentProcessor.edit_output(updated_guide_compared)
    #     else:
    #         DocumentProcessor.display_output(outdated_guide_compared, updated_guide_compared)
    #
    #     def regenerate_guide():
    #         st.session_state.generated_text = DocumentProcessor.generate_text(prompt,
    #                                                                           st.session_state.outdated_guide_text,
    #                                                                           st.session_state.reference_material_text)
    #
    #     st.button("Re-Generate", on_click=regenerate_guide)
    #
    #     st.subheader("Download the Updated User Guide")
    #
    #     # st.selectbox("Export As...",
    #     #              ("DOCX", "TXT", "PDF", "PPT", "MP4"))
    #
    #     st.download_button(
    #         "Download",
    #         file_name="updated_guide.txt",
    #         data=st.session_state.generated_text
    #     )


if __name__ == "__main__":
    main()
