import streamlit as st
from utilities.document_retriever import DocumentRetriever


@st.cache_data
def cached_rag_retrieval(outdated_guide, reference_material, additional_reference):
    doc_generator = DocumentRetriever()
    return doc_generator.rag_retrieval(outdated_guide, reference_material, additional_reference)


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


def add_entry():
    if st.session_state.new_entry.strip():
        st.session_state.additional_entries.append(st.session_state.new_entry.strip())
        # Reset text input
        st.session_state.new_entry = ""


def remove_entry(index):
    st.session_state.additional_entries.pop(index)


def run_update_tab():
    # Initialize session state variables
    st.session_state.setdefault('retrieved', None)
    st.session_state.setdefault('outer_count', 0)
    st.session_state.setdefault('inner_count', 0)
    st.session_state.setdefault('additional_entries', [])

    with st.container(border=True):
        st.subheader("Upload Training Material")
        outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["docx", "pdf"])

    with st.container(border=True):
        st.subheader("Upload Reference Material")
        reference_material_file = st.file_uploader("Choose the reference material document", type=["docx", "pdf"])

        # Toggle button to display additional reference entries feature
        on = st.toggle("Add Reference Entry")
        if on:
            col1, col2 = st.columns([8, 1])

            # Text input for additional entries
            with col1:
                st.text_input(label="Enter updates for training material", key="new_entry",
                              label_visibility="collapsed")
            with col2:
                st.button("Add Entry", on_click=add_entry, use_container_width=True)

        # Display current additional entries
        if st.session_state.additional_entries:
            st.write("Current additional entries:")
            for i, entry in enumerate(st.session_state.additional_entries):
                col1, col2 = st.columns([8, 1])
                with col1:
                    st.write(f"{i + 1}. {entry}")
                with col2:
                    # Bottom to remove additional entry
                    st.button("Remove", key=f"remove_entry{i}", on_click=remove_entry, args=(i,),
                              use_container_width=True)

    if st.button("Generate Updated Guide"):
        if outdated_guide_file is None:
            st.error("Please upload outdated material.")
        elif reference_material_file is None:
            st.error("Please upload reference material")
        else:
            with st.spinner("Retrieving Sections..."):
                st.session_state.retrieved = cached_rag_retrieval(
                    outdated_guide_file,
                    reference_material_file,
                    st.session_state.additional_entries
                )
            st.session_state.outer_count = 0
            st.session_state.inner_count = 0
            st.success("Sections Retrieved!")

    # Navigation and content display
    with st.container(border=True):
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
