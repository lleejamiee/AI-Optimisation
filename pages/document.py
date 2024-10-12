import streamlit as st

from utilities.document_update import run_update_tab
from utilities.document_create import run_create_tab


def main():
    st.set_page_config(page_title="Documents", layout="wide")

    tab1, tab2 = st.tabs(["Update", "Create"])

    with tab1:
        st.header("Update Document")
        run_update_tab()

    with tab2:
        st.header("Create Document")
        run_create_tab()


if __name__ == "__main__":
    main()
