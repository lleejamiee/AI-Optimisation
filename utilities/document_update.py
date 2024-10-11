import streamlit as st
from utilities.document_retriever import DocumentRetriever


def cached_rag_retrieval(outdated_guide, reference_material):
    doc_generator = DocumentRetriever()
    return doc_generator.rag_retrieval(outdated_guide, reference_material)


def next_section():
    if st.session_state.inner_count + 1 < len(st.session_state.retrieved[st.session_state.outer_count]):
        st.session_state.inner_count += 1
    elif st.session_state.outer_count + 1 < len(st.session_state.retrieved):
        st.session_state.outer_count += 1
        st.session_state.inner_count = 0


def previous_section():
    if st.session_state.inner_count > 0:
        st.session_state.inner_count -= 1
    elif st.session_state.outer_count > 0:
        st.session_state.outer_count -= 1
        st.session_state.inner_count = len(st.session_state.retrieved[st.session_state.outer_count]) - 1


def run_update_tab():
    # Initialize session state variables
    st.session_state.setdefault('retrieved', None)
    st.session_state.setdefault('outer_count', 0)
    st.session_state.setdefault('inner_count', 0)

    col1, col2 = st.columns(2)
    with col1:
        outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["docx"])
    with col2:
        reference_material_file = st.file_uploader("Choose the reference material document", type=["docx"])

    if st.button("Generate Updated Guide"):
        if outdated_guide_file is None:
            st.error("Please upload outdated material.")
        elif reference_material_file is None:
            st.error("Please upload reference material")
        else:
            with st.spinner("Retrieving Sections..."):
                st.session_state.retrieved = cached_rag_retrieval(outdated_guide_file, reference_material_file)
            st.session_state.outer_count = 0
            st.session_state.inner_count = 0
            st.success("Sections Retrieved!")

    # Navigation and content display
    if st.session_state.retrieved is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("⏮️ Previous", on_click=previous_section)
        with col2:
            st.write(
                f"Section {st.session_state.outer_count + 1} of {len(st.session_state.retrieved)}, "
                f"Subsection {st.session_state.inner_count + 1} of "
                f"{len(st.session_state.retrieved[st.session_state.outer_count])}"
            )
        with col3:
            st.button("Next ⏭️", on_click=next_section)

        # Display content
        section = st.session_state.retrieved[st.session_state.outer_count][st.session_state.inner_count]
        st.subheader(f"Section {st.session_state.outer_count + 1}.{st.session_state.inner_count + 1}")
        st.write(section.text)
