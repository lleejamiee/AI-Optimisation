import streamlit as st
from utilities.powerpoint import PowerPoint


def main():
    st.set_page_config(page_title="PowerPoint", layout="wide")

    tab1, tab2 = st.tabs(["Update", "Create"])

    # First tab is used to update an existing PowerPoint document
    with tab1:
        st.header("Update PowerPoint")

        with st.expander("Description"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Process")
                st.markdown("""
                1. Upload existing PowerPoint file
                2. Provide update instructions or new content
                4. Review AI-suggested changes
                5. Make manual edits if needed
                6. Export updated PowerPoint
                """)
            with col2:
                st.write("")
                st.subheader("Features")
                st.markdown("""
                - AI-powered slide content updating
                - Preview changes before applying
                - Manual edit option
                """)

        # Ctrl + click on update_slide() to view more details
        PowerPoint.update_slide()

    # Second tab is used to create a new PowerPoint document
    with tab2:
        st.header("Create PowerPoint")

        with st.expander("Description"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Process")
                st.markdown("""
                1. Upload any files to base the powerpoint on
                2. Specify how you want the content be created
                3. Generate powerpoint slides
                4. Export powerpoint slides
                """)
            with col2:
                st.write("")
                st.subheader("Features")
                st.markdown("""
                - AI-powered document updating
                - Multiple input sources (files, webpages)
                """)

        # Ctrl + click on create_slide() to view more details
        PowerPoint.create_slide()

if __name__ == "__main__":
    main()
