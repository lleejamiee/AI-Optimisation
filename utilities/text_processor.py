from openai import OpenAI
import requests
import docx2txt
import streamlit as st
import pdfplumber
from bs4 import BeautifulSoup
from urllib.request import urlopen
import certifi
import ssl

class TextProcessor:

    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    def generate_text(prompt, outdated_guide, reference_material):
        history = [
            {"role": "system",
             "content": prompt},
            {"role": "user",
             "content": f"Outdated User Guide:\n{outdated_guide}\n\nReference Material:\n{reference_material}"}
        ]

        completion = TextProcessor.client.chat.completions.create(
            model="model-identifier",
            messages=history,
            temperature=0.7,
            stream=True
        )

        generated_text = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0] and chunk.choices[0].delta and chunk.choices[0].delta.content:
                generated_text += chunk.choices[0].delta.content

        return generated_text

    def extract_text(file):
        if file.type == "text/plain":
            file_text = str(file.read(), "utf-8")
        elif file.type == "application/pdf":
            try:
                with pdfplumber.open(file) as pdf:
                    pages = pdf.pages[0]
                    file_text = pages.extract_text()
            except:
                return
        else:
            file_text = docx2txt.process(file)

        return file_text

    def extract_url_text(url):
        try:
            resp = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
            context = ssl._create_unverified_context()
            response = urlopen(url, context=context)
            html = (response.read())

            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string

            headings = [h.get_text() for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"])]

            content = " ".join(headings)

            return content

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

    def handle_updated_guide(updated_guide):
        st.write(updated_guide)

        st.subheader("Download the Updated User Guide")

        # Create .docx file
        with open("updated_guide.docx", "w") as f:
            # Write from generated text
            f.write(updated_guide)

        # Allow app user to download .docx file(updated user guide file) containing generated text
        st.download_button("Download", updated_guide)

    def read_files(outdated_guide_file, reference_material_file):
        if outdated_guide_file is not None and reference_material_file is not None:
            outdated_guide_text = TextProcessor.extract_text(outdated_guide_file)
            reference_material_text = TextProcessor.extract_text(reference_material_file)

            return outdated_guide_text, reference_material_text
        else:
            st.error("Please upload both files.")
            return None, None

    def edit_output(updated_guide):
        # Display the text area for editing
        edited_text = st.text_area("Edit the content", height=800, value=st.session_state.generated_text,
                                   key="edit_area")

        # Save the changes
        if st.button("Save Changes"):
            st.session_state.generated_text = edited_text
            st.success("Changes saved successfully!")
            st.session_state.edit_mode = False
            st.rerun()

    def display_output(updated_guide):
        st.write(st.session_state.generated_text)

        if st.button("Edit this output"):
            st.session_state.edit_mode = True
            st.rerun()