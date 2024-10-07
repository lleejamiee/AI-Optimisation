import streamlit as st

from utilities.powerpoint import PowerPoint


def main():
    st.set_page_config(page_title="PowerPoint", layout="wide")

    tab1, tab2 = st.tabs(["Update", "Create"])

    with tab1:
        # Set app header
        st.header("Update PowerPoint")

        PowerPoint.update_slide()

    with tab2:
        st.header("Create PowerPoint")

        PowerPoint.create_slide()

if __name__ == "__main__":
    main()
