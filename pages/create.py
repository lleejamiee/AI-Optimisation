import requests
from openai import OpenAI
import streamlit as st
from utilities.text_processor import TextProcessor

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

def main():
    st.set_page_config(page_title="User Guide Updater")

    # Set app header
    st.header("Create a user guide")

    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["txt", "pdf", "docx"])
    reference_material_file = st.file_uploader("Choose the reference material document", type=["txt", "pdf", "docx"])
    webpage_link = st.text_input("Input webpage link")

    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = None

    if st.button("Generate Updated Guide"):
        if outdated_guide_file is not None:
            #st.write(outdated_guide_text)

            if reference_material_file or webpage_link is not None:
                if reference_material_file:
                    outdated_guide_text, reference_material_text = TextProcessor.read_files(outdated_guide_file, reference_material_file)
                    st.session_state.generated_text = TextProcessor.generate_text(prompt, outdated_guide_text,
                                                                                  reference_material_text)
                    #st.write(reference_material_text)

                if webpage_link:
                    outdated_guide_text = TextProcessor.extract_text(outdated_guide_file)
                    reference_material_text = TextProcessor.extract_url_text(webpage_link)
                    st.session_state.generated_text = TextProcessor.generate_text(prompt, outdated_guide_text,
                                                                                  reference_material_text)
                    #st.write(reference_material_text)

            else:
                st.error("Please upload either reference material or webpage link.")

        else:
            st.error("Please upload outdated material.")

    st.subheader("Updated User Guide Content")

    if st.session_state.generated_text:

        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False

        if st.session_state.edit_mode:
            TextProcessor.edit_output(st.session_state.generated_text)
        else:
            TextProcessor.display_output(st.session_state.generated_text)

        def regenerate_guide():
            st.session_state.generated_text = TextProcessor.generate_text(prompt, outdated_guide_text, reference_material_text)

        st.button("Re-Generate", on_click=regenerate_guide)
        st.subheader("Download the Updated User Guide")

        # Allow app user to download .docx file(updated user guide file) containing generated text
        st.download_button(
            "Download",
            file_name="updated_guide.txt",
            data=st.session_state.generated_text
        )


if __name__ == '__main__':
    main()
