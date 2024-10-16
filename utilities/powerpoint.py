from io import BytesIO
import streamlit as st
from utilities.slide_generator import SlideGenerator
from utilities.slide_processor import SlideProcessor


class PowerPoint:
    # The method update_slide handles the user interface side of the feature.
    def update_slide(**kwargs):
        # Upload both outdated user guide and reference material
        outdated_guide_file = st.file_uploader("Choose the outdated user guide document",
                                               type=["pptx"])
        reference_material_file = st.file_uploader("Choose the reference material document",
                                                   type=["txt", "pdf", "docx", "pptx"])
        webpage_link = st.text_input("Input webpage link")

        # When 'Generate New PowerPoint' button is clicked
        if st.button("Generate Updated Guide"):
            if outdated_guide_file is not None:
                # Outdated document is saved locally
                st.session_state.outdated_path = SlideGenerator.save_uploaded_file(outdated_guide_file)

                # Reference material (either a file or a webpage link) is parsed as a document for LLM
                if reference_material_file or webpage_link is not None:
                    if reference_material_file:
                        reference_path = SlideGenerator.save_uploaded_file(reference_material_file)
                        st.session_state.reference_document = SlideGenerator.load_reference(reference_path)

                    if webpage_link:
                        st.session_state.reference_document = SlideGenerator.load_webpage(webpage_link)

            if 'outdated_path' and 'reference_document' in st.session_state:
                # Update is generated by LLM
                st.session_state.ppt, st.session_state.contents_map = SlideGenerator.generate_updated(
                    st.session_state.outdated_path, st.session_state.reference_document)
                # Original document and updated document are compared
                SlideProcessor.compare_difference()

            elif not outdated_guide_file:
                st.error("Please upload outdated material.")

            if not reference_material_file or webpage_link:
                st.error("Please upload a reference document or an URL.")

        if 'before' and 'after' in st.session_state:
            st.subheader("Updated User Guide Content")

            # When 'Edit' button is clicked, the interface turns into edit mode
            if "edit_mode" not in st.session_state:
                st.session_state.edit_mode = False

            if not st.session_state.edit_mode:
                # Before and after are displayed side by side
                SlideProcessor.display_difference(st.session_state.before, st.session_state.after)
                if st.button("Edit"):
                    st.session_state.edit_mode = True
                    st.rerun()
            else:
                SlideProcessor.edit_output()

            # PowerPoint document gets modified, so it's ready to be downloaded
            SlideProcessor.modify_powerpoint()

            binary_output = BytesIO()
            st.session_state.ppt.save(binary_output)

            st.subheader("Download the Updated User Guide")

            # When the download button is clicked, the PowerPoint document gets downloaded
            st.download_button(
                "Download",
                key="update",
                file_name="updated_guide.pptx",
                data=binary_output,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

    # The method create_slide handles the user interface side of the feature.
    def create_slide(**kwargs):
        # Users can upload multiple files as reference material
        uploaded_files = st.file_uploader("Upload files to generate a new PowerPoint", accept_multiple_files=True)
        # Users can enter prompt to give the LLM more specific instruction
        prompt = st.text_input("Enter your prompt\n\nExample: Create a 10-slide presentation on the given content. Use "
                               "a friendly and engaging tone")

        # When 'Generate New PowerPoint' button is clicked
        if st.button("Generate New PowerPoint"):
            if uploaded_files and prompt:
                file_paths = []
                for uploaded_file in uploaded_files:
                    # Uploaded files are saved locally
                    file_paths.append(SlideGenerator.save_uploaded_file(uploaded_file))

                reference_docs = []
                for path in file_paths:
                    # The files are then parsed as documents for LLM
                    reference_docs.append(SlideGenerator.load_reference(path))

                # Parsed documents, and prompts are passed to LLM to generate a reply
                reply = SlideGenerator.generate_new(reference_docs, prompt)
                st.session_state.slide_data = SlideGenerator.extract_json(reply)

            elif not uploaded_files:
                st.error("Please upload files.")
            elif not prompt:
                st.error("Please enter your prompt.")

        # Once a new PowerPoint document has been created, the user can view the content
        if 'slide_data' in st.session_state:
            st.subheader("Generated PowerPoint")
            contents = SlideProcessor.json_to_string()
            st.markdown("<br>".join(contents), unsafe_allow_html=True)

            new = SlideProcessor.create_slides()
            binary_output = BytesIO()
            new.save(binary_output)

            st.subheader("Download the new PowerPoint")

            # When the download button is clicked, the PowerPoint document gets downloaded
            st.download_button(
                "Download",
                key="create",
                file_name="updated_guide.pptx",
                data=binary_output,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
