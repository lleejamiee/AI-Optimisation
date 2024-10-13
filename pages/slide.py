import streamlit as st
from utilities.powerpoint import PowerPoint


def main():
    st.set_page_config(page_title="PowerPoint", layout="wide")

    tab1, tab2 = st.tabs(["Update", "Create"])

    # First tab is used to update an existing PowerPoint document
    with tab1:
        st.header("Update PowerPoint")

        # Ctrl + click on update_slide() to view more details
        PowerPoint.update_slide()

    # Second tab is used to create a new PowerPoint document
    with tab2:
        st.header("Create PowerPoint")

        # Ctrl + click on create_slide() to view more details
        PowerPoint.create_slide()

if __name__ == "__main__":
    main()
