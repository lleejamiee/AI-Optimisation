from utilities.document_processor import DocumentProcessor
import streamlit as st

# Prompt for LLM
prompt = """
You are a technical writer tasked with creating a user guide for a product/service. 
Your task is to create a user guide by incorporating relevant information from the provided outdated user guide, and the reference material.
Only generate the content that is to be used in this new user guide.
Do not provide explanations or notes.

The user will input one text document
Document 1: Outdated User Guide
Document 2: Reference Material
"""


def run_create_tab():
    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["txt", "pdf", "docx"])
    reference_material_file = st.file_uploader("Choose the reference material document", type=["txt", "pdf", "docx"])
    webpage_link = st.text_input("Input webpage link")

    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = None

    if st.button("Generate Updated Guide", key="generate"):
        if outdated_guide_file is not None:
            # st.write(outdated_guide_text)

            if reference_material_file or webpage_link is not None:
                if reference_material_file:
                    st.session_state.outdated_guide_text, st.session_state.reference_material_text = DocumentProcessor.read_files(
                        outdated_guide_file, reference_material_file)
                    st.session_state.generated_text = DocumentProcessor.generate_text(prompt,
                                                                                      st.session_state.outdated_guide_text,
                                                                                      st.session_state.reference_material_text)
                    # st.write(reference_material_text)

                if webpage_link:
                    st.session_state.outdated_guide_text = DocumentProcessor.extract_text(outdated_guide_file)
                    st.session_state.reference_material_text = DocumentProcessor.extract_url_text(webpage_link)
                    st.session_state.generated_text = DocumentProcessor.generate_text(prompt,
                                                                                      st.session_state.outdated_guide_text,
                                                                                      st.session_state.reference_material_text)
                    # st.write(reference_material_text)

            else:
                st.error("Please upload either reference material or webpage link.")

        else:
            st.error("Please upload outdated material.")

    st.subheader("Updated User Guide Content")

    if st.session_state.generated_text:

        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False

        outdated_guide_compared, updated_guide_compared = DocumentProcessor.compare_texts(
            st.session_state.outdated_guide_text,
            st.session_state.generated_text)

        if st.session_state.edit_mode:
            DocumentProcessor.edit_output(updated_guide_compared)
        else:
            DocumentProcessor.display_output(outdated_guide_compared, updated_guide_compared)

        def regenerate_guide():
            st.session_state.generated_text = DocumentProcessor.generate_text(prompt,
                                                                              st.session_state.outdated_guide_text,
                                                                              st.session_state.reference_material_text)

        st.button("Re-Generate", key="regenerate", on_click=regenerate_guide)

        DocumentProcessor.select_version()

        st.subheader("Download the Updated User Guide")

        st.selectbox("Export As...",
                     ("DOCX", "TXT", "PDF", "PPT", "MP4"))

        st.download_button(
            "Download",
            file_name="updated_guide.txt",
            data=st.session_state.generated_text
        )
