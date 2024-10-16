import streamlit as st
from utilities.document_retriever import DocumentRetriever
from utilities.document_updater import prepare_updated_document, temp_file
import difflib


@st.cache_data
def cached_rag_retrieval(outdated_guide, reference_material=None, additional_search_text=None):
    doc_generator = DocumentRetriever()
    return doc_generator.rag_retrieval(outdated_guide, reference_material, additional_search_text)


def add_entry():
    if st.session_state.new_entry.strip():
        st.session_state.additional_entries.append(st.session_state.new_entry.strip())
        # Reset text input
        st.session_state.new_entry = ""


def remove_entry(index):
    st.session_state.additional_entries.pop(index)


def next_item(ref_index):
    if st.session_state[f'current_index_{ref_index}'] < len(st.session_state.retrieved[ref_index]['retrieved']) - 1:
        st.session_state[f'current_index_{ref_index}'] += 1


def prev_item(ref_index):
    if st.session_state[f'current_index_{ref_index}'] > 0:
        st.session_state[f'current_index_{ref_index}'] -= 1


def remove_row(index):
    st.session_state.retrieved.pop(index)


def update_sections():
    doc_retriever = DocumentRetriever()
    sections_to_update = []

    for i, pair in enumerate(st.session_state.retrieved):
        current_index = st.session_state[f'current_index_{i}']
        section = {
            'reference': pair['reference'],
            'retrieved': pair['retrieved'][current_index]
        }
        sections_to_update.append(section)
    with st.spinner("Updating Sections..."):
        # LLM inference with context pair data
        updated_sections = doc_retriever.update_sections(sections_to_update)

    # Save LLM response
    st.session_state.updated_sections = updated_sections
    st.rerun()


def highlight_diff(text1, text2):
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()
    differ = difflib.Differ()
    diff = list(differ.compare(text1_lines, text2_lines))
    text1_output = []
    text2_output = []

    for line in diff:
        if line.startswith("  "):  # Unchanged line
            text1_output.append(line[2:].rstrip())
            text2_output.append(line[2:].rstrip())
        elif line.startswith("- "):  # Line only in text1
            text1_output.append(f'<span style="background-color: #ffcccc">{line[2:]}</span>')
        elif line.startswith("+ "):  # Line only in text2
            text2_output.append(f'<span style="background-color: #ccffcc">{line[2:]}</span>')
        elif line.startswith("? "):  # Hint line, ignore
            continue

    return '\n'.join(text1_output), '\n'.join(text2_output)


def run_update_tab():
    # Initialize session state variables
    if 'retrieved' not in st.session_state:
        st.session_state.retrieved = None
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = True
    if 'additional_entries' not in st.session_state:
        st.session_state.additional_entries = []

    if st.session_state.show_upload:
        # File upload section
        with st.container(border=True):
            st.subheader("Upload Training Material")
            outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["docx", "pdf"])
            if outdated_guide_file is not None:
                st.session_state.outdated_guide_file_path = temp_file(outdated_guide_file)
        with st.container(border=True):
            st.subheader("Upload Reference Material")
            reference_material_file = st.file_uploader("Choose the reference material document", type=["docx", "pdf", "txt"])

            # Additional entries for Reference Material
            with st.expander("Add Reference Entry"):
                col1, col2 = st.columns([8, 1])
                # Text input field for additional entries
                with col1:
                    st.text_input(label="Enter updates for training material", key="new_entry",
                                  label_visibility="collapsed")
                with col2:
                    st.button("Add Entry", on_click=add_entry, use_container_width=True)

                # Display current additional entries if there are any
                if st.session_state.additional_entries:
                    st.write("Current reference entries:")
                    for i, entry in enumerate(st.session_state.additional_entries):
                        col1, col2 = st.columns([8, 1])
                        with col1:
                            st.write(f"{i + 1}. {entry}")
                        with col2:
                            # Button to remove additional entry
                            st.button("Remove", key=f"remove_entry{i}",
                                      on_click=remove_entry, args=(i,),
                                      use_container_width=True)

        # Button to retrieve sections
        if st.button("Retrieve Sections"):
            if outdated_guide_file is None:
                st.error("Please upload outdated material.")
                return
            elif reference_material_file is None and not st.session_state.additional_entries:
                st.error("Please include reference material")
            else:
                with st.spinner("Retrieving Sections..."):
                    # Perform retrieval and store in session state
                    st.session_state.retrieved = cached_rag_retrieval(
                        outdated_guide_file,
                        reference_material=reference_material_file,
                        additional_search_text=st.session_state.additional_entries
                    )
                # Update to hide file upload
                st.session_state.show_upload = False
                st.rerun()

    with st.container(border=True):
        if st.session_state.retrieved is not None:
            # Display retrieved data
            st.subheader("Retrieved Items")
            col1, col2, col3, col4 = st.columns([4, 5, 1, 1])
            col1.write("**Reference**")
            col2.write("**Retrieved Text**")
            col3.write("**Navigation**")
            col4.write("**Action**")

            # Display relevant data in a row for each retrieved section
            for i, pair in enumerate(st.session_state.retrieved):
                # Initialize current index for this reference if not exists
                if f'current_index_{i}' not in st.session_state:
                    st.session_state[f'current_index_{i}'] = 0

                col1, col2, col3, col4 = st.columns([4, 5, 1, 1])
                # Display reference content
                with col1:
                    st.write(pair['reference'])
                # Display retrieved content
                with col2:
                    # Item at index 'i' is displayed
                    current_item = pair['retrieved'][st.session_state[f'current_index_{i}']]
                    st.write(current_item.text)
                # Navigation buttons to traverse through retrieved sections
                with col3:
                    prev_col, index_col, next_col = st.columns([1, 1, 1])
                    with prev_col:
                        st.button("◀", key=f"prev_{i}", on_click=prev_item, args=(i,))
                    with index_col:
                        current_index = st.session_state[f'current_index_{i}'] + 1
                        total_items = len(pair['retrieved'])
                        st.write(f"{current_index}/{total_items}")
                    with next_col:
                        st.button("▶", key=f"next_{i}", on_click=next_item, args=(i,))
                with col4:
                    st.button("Remove", key=f"remove_{i}", on_click=remove_row, args=(i,))

                if pair != st.session_state.retrieved[-1]:
                    st.write("---")

    if st.session_state.retrieved is not None:
        # Button to perform inference using reference and retrieved section data
        if st.button("Update All Sections"):
            if st.session_state.retrieved:
                update_sections()

    if 'updated_sections' in st.session_state and st.session_state.updated_sections:
        # Display updated sections
        st.header("Updated Sections")

        with st.container(border=True):
            st.subheader("Content Comparison")
            # Display data in a row for each updated section
            for section in st.session_state.updated_sections:
                # Highlight differences between texts
                highlighted_original, highlighted_updated = highlight_diff(
                    section['original_content'],
                    section['updated_content']
                )
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Original Content**")
                    st.write(highlighted_original, unsafe_allow_html=True)
                with col2:
                    st.write("**Updated Content**")
                    st.write(highlighted_updated, unsafe_allow_html=True)
                if section != st.session_state.updated_sections[-1]:
                    st.write("---")

        # Button to update document content
        if st.button("Generate Updated Document"):
            if st.session_state.outdated_guide_file_path:
                updated_file_data, updated_filename = prepare_updated_document(
                    st.session_state.outdated_guide_file_path,
                    st.session_state.updated_sections
                )

                # Button to download updated file
                st.download_button(
                    label="Download Updated Document",
                    data=updated_file_data,
                    file_name=updated_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )