import streamlit as st

from utilities.document_update_tab import run_update_tab
from utilities.document_create_tab import run_create_tab


def main():
    st.set_page_config(page_title="Documents", layout="wide")

    tab1, tab2 = st.tabs(["Update", "Create"])

    with tab1:
        col1, col2, col3 = st.columns([2, 8, 1])
        with col1:
            st.header("Update Document")

        with col3:
            if st.button("Refresh", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        run_update_tab()

    with tab2:
        st.header("Create Document")
        run_create_tab()


if __name__ == "__main__":
    main()
