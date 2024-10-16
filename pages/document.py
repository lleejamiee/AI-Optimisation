import streamlit as st

from utilities.document_update_tab import run_update_tab
from utilities.document_create_tab import run_create_tab


def main():
    st.set_page_config(page_title="Documents", layout="wide")

    tab1, tab2 = st.tabs(["Update", "Create"])

    # Update tab
    with tab1:
        col1, col2 = st.columns([11, 1])

        with col1:
            st.header("Document Updating")

        with col2:
            if st.button("Refresh", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        with st.expander("Description"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Steps")
                st.markdown("""
                1. Upload your document
                2. Provide any additional context or instructions
                3. Review AI-suggested updates
                4. Make any necessary edits
                5. Download your updated document
                """)
            with col2:
                st.write("")
                st.subheader("Features")
                st.markdown("""
                - Upload existing documents
                - Provide reference material for updates
                - AI-assisted document updating
                - Review and edit suggested changes
                """)

        run_update_tab()

    # Create tab
    with tab2:
        st.header("Document Recreating")

        with st.expander("Description"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Steps")
                st.markdown("""
                1. Upload outdated user guide
                2. Provide reference material or webpage link
                3. Generate updated guide using AI
                4. Review and edit AI-suggested updates
                5. Select preferred version
                6. Export and download updated guide
                """)

            with col2:
                st.subheader("Features")
                st.markdown("""
                - AI-powered document updating
                - Multiple input sources (files, webpages)
                - Side-by-side comparison view
                - Edit mode for refining content
                - Version selection
                - Multiple export formats (DOCX, TXT, PDF, PPT, MP4)
                - Automated technical documentation updating
                """)

        run_create_tab()


if __name__ == "__main__":
    main()