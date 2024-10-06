from io import BytesIO
import streamlit as st
from utilities.slide_generator import SlideGenerator
from utilities.slide_processor import SlideProcessor


class PowerPoint:
    def update_slide(**kwargs):
        # Upload both outdated user guide and reference material
        outdated_guide_file = st.file_uploader("Choose the outdated user guide document",
                                               type=["txt", "pdf", "docx", "pptx"])
        reference_material_file = st.file_uploader("Choose the reference material document",
                                                   type=["txt", "pdf", "docx", "pptx"])
        webpage_link = st.text_input("Input webpage link")

        if st.button("Generate Updated Guide"):
            if outdated_guide_file is not None:
                st.session_state.outdated_path = SlideGenerator.save_uploaded_file(outdated_guide_file)

                if reference_material_file or webpage_link is not None:
                    if reference_material_file:
                        reference_path = SlideGenerator.save_uploaded_file(reference_material_file)
                        st.session_state.reference_document = SlideGenerator.load_reference(reference_path)

                    if webpage_link:
                        st.session_state.reference_document = SlideGenerator.load_webpage(webpage_link)

            if 'outdated_path' and 'reference_document' in st.session_state:
                st.session_state.ppt, st.session_state.contents_map = SlideGenerator.generate_updated(
                    st.session_state.outdated_path, st.session_state.reference_document)
                SlideProcessor.compare_difference()

            elif not outdated_guide_file:
                st.error("Please upload outdated material.")

            if not reference_material_file or webpage_link:
                st.error("Please upload a reference document or an URL.")

        if 'before' and 'after' in st.session_state:
            st.subheader("Updated User Guide Content")

            if "edit_mode" not in st.session_state:
                st.session_state.edit_mode = False

            if not st.session_state.edit_mode:
                SlideProcessor.display_difference(st.session_state.before, st.session_state.after)
                if st.button("Edit"):
                    st.session_state.edit_mode = True
                    st.rerun()
            else:
                SlideProcessor.edit_output()

            SlideProcessor.modify_powerpoint()

            binary_output = BytesIO()
            st.session_state.ppt.save(binary_output)

            st.subheader("Download the Updated User Guide")

            st.download_button(
                "Download",
                file_name="updated_guide.pptx",
                data=binary_output,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

    def create_slide(**kwargs):
        uploaded_files = st.file_uploader("Upload files to generate a new PowerPoint", accept_multiple_files=True)
        prompt = st.text_input("Enter your prompt")

        if st.button("Generate New PowerPoint"):
            if uploaded_files and prompt:
                file_paths = []
                for uploaded_file in uploaded_files:
                    file_paths.append(SlideGenerator.save_uploaded_file(uploaded_file))

                reference_docs = []
                for path in file_paths:
                    reference_docs.append(SlideGenerator.load_reference(path))

                reply = SlideGenerator.generate_new(reference_docs, prompt)
                st.session_state.slide_data = SlideGenerator.extract_json(reply)

            elif not uploaded_files:
                st.error("Please upload files.")
            elif not prompt:
                st.error("Please enter your prompt.")

        if 'slide_data' in st.session_state:
            st.subheader("Generated PowerPoint")
            contents = SlideProcessor.json_to_string()
            st.markdown("<br>".join(contents), unsafe_allow_html=True)

            new = SlideProcessor.create_slides()
            binary_output = BytesIO()
            new.save(binary_output)

            st.subheader("Download the new PowerPoint")

            st.download_button(
                "Download",
                file_name="updated_guide.pptx",
                data=binary_output,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
