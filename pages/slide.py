from io import BytesIO
import streamlit as st
from utilities.slide_rag import SlideRag


def main():
    st.set_page_config(page_title="Update PowerPoint", layout="wide")

    # Set app header
    st.header("Update PowerPoint")

    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide document",
                                           type=["txt", "pdf", "docx", "pptx"])
    reference_material_file = st.file_uploader("Choose the reference material document",
                                               type=["txt", "pdf", "docx", "pptx"])
    webpage_link = st.text_input("Input webpage link")

    if st.button("Generate Updated Guide"):
        if outdated_guide_file is not None:
            st.session_state.outdated_path = SlideRag.save_uploaded_file(outdated_guide_file)

            if reference_material_file or webpage_link is not None:
                if reference_material_file:
                    reference_path = SlideRag.save_uploaded_file(reference_material_file)
                    st.session_state.reference_document = SlideRag.load_reference(reference_path)

                if webpage_link:
                    st.session_state.reference_document = SlideRag.load_webpage(webpage_link)
            else:
                st.error("Please upload either reference material or webpage link.")

        if 'outdated_path' and 'reference_document' in st.session_state:
            st.session_state.ppt, st.session_state.contents_map = SlideRag.generate_updated(
                st.session_state.outdated_path, st.session_state.reference_document)
            SlideRag.compare_difference()

        else:
            st.error("Please upload outdated material.")

    if 'before' and 'after' in st.session_state:
        st.subheader("Updated User Guide Content")

        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

        if not st.session_state.edit_mode:
            SlideRag.display_difference(st.session_state.before, st.session_state.after)
            if st.button("Edit"):
                st.session_state.edit_mode = True
                st.rerun()
        else:
            SlideRag.edit_output()

        SlideRag.modify_powerpoint()
        binary_output = BytesIO()
        st.session_state.ppt.save(binary_output)

        st.subheader("Download the Updated User Guide")

        st.download_button(
            "Download",
            file_name="updated_guide.pptx",
            data=binary_output,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )


if __name__ == "__main__":
    main()
