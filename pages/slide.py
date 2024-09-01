import streamlit as st
from utilities.slide_processor import SlideProcessor

# query_json = """{
#     "input_text": "[[content]]",
#     "output_format": "json",
#     "json_structure": {
#     "slide.py": "{{presentation_slides}}"
#     }
# }"""
#
# # Prompt for LLM
# prompt = """
# You are a technical writer tasked with creating a user guide for a product/service.
# Your task is to update a user guide powerpoint by incorporating relevant information from the provided outdated user guide, and the reference material.
# Only generate the content that is to be used in this new user guide.
# Do not provide explanations or notes.
#
# The user will input one text document
# Document 1: Outdated User Guide
# Document 2: Reference Material
# """


def main():
    st.set_page_config(page_title="Update PowerPoint", layout="wide")

    # Set app header
    st.header("Update PowerPoint")

    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["pptx"])
    reference_material_file = st.file_uploader("Choose the reference material document", type=["txt", "pdf", "docx", "pptx"])
    webpage_link = st.text_input("Input webpage link")

    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = None

    if st.button("Generate Updated Guide"):
        if outdated_guide_file is not None:
            outdated_path = SlideProcessor.save_uploaded_file(outdated_guide_file)
            st.session_state.outdated_doc = SlideProcessor.load_document(outdated_path)

            if reference_material_file or webpage_link is not None:
                if reference_material_file:
                    reference_path = SlideProcessor.save_uploaded_file(reference_material_file)
                    st.session_state.reference_doc = SlideProcessor.load_document(reference_path)

                if webpage_link:
                    st.session_state.reference_doc = SlideProcessor.load_webpage(webpage_link)
            else:
                st.error("Please upload either reference material or webpage link.")

        else:
            st.error("Please upload outdated material.")

    if 'outdated_doc' and 'reference_doc' in st.session_state:
        print("I'm here")
        # s_engine = SlideProcessor.build_query_engine(st.session_state.outdated_doc, st.session_state.reference_doc)


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
    #         st.session_state.generated_text = SlideProcessor.generate_presentation_content(st.session_state.outdated_guide_text, st.session_state.reference_material_text)
    #
    #     st.button("Re-Generate", on_click=regenerate_guide)
    #
    #     # TextProcessor.select_version()
    #
    #     # outdated_guide_slide = Presentation(outdated_guide_file)
    #     # formatting_data = [SlideProcessor.extract_formatting(slide) for slide in outdated_guide_slide.slides]
    #     # slide_data = SlideProcessor.generate_presentation(st.session_state.generated_text, formatting_data)
    #     slide_data = SlideProcessor.create_slides(st.session_state.generated_text)
    #     binary_output = BytesIO()
    #     slide_data.save(binary_output)
    #
    #     st.subheader("Download the Updated User Guide")
    #
    #     # st.selectbox("Export As...",
    #     #              ("DOCX", "TXT", "PDF", "PPT", "MP4"))
    #
    #     st.download_button(
    #         "Download",
    #         file_name="updated_guide.pptx",
    #         data=binary_output,
    #         mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    #     )


if __name__ == "__main__":
    main()
