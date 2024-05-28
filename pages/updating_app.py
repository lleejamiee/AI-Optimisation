from openai import OpenAI
import docx2txt
import streamlit as st
import pdfplumber

# Initialize OpenAI client with local inference server (LM Studio)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Prompt for LLM
prompt = """
You are a technical writer tasked with updating an outdated user guide for a product/service. 
Your task is to update an outdated user guide by incorporating relevant information from the provided reference material.
Only generate the content that is to be used in this updated user guide.
Do not provide explanations or notes.

The user will input two text documents
Document 1: Outdated User Guide
Document 2: Reference Material
"""


# llm on local inference server(LM Studio)
def generate_text(outdated_guide, reference_material):
    history = [
        {"role": "system",
         "content": prompt},
        {"role": "user",
         "content": f"Outdated User Guide:\n{outdated_guide}\n\nReference Material:\n{reference_material}"}
    ]

    completion = client.chat.completions.create(
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


def main():
    st.set_page_config(page_title="User Guide Updater")

    # Set app header
    st.header("Update a user guide")

    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide document", type=["txt", "pdf", "docx"])
    reference_material_file = st.file_uploader("Choose the reference material document", type=["txt", "pdf", "docx"])

    if outdated_guide_file is not None and reference_material_file is not None:
        outdated_guide_text = extract_text(outdated_guide_file)
        reference_material_text = extract_text(reference_material_file)

        # Uncomment to display the contents of each .docx file on the app
        st.write(outdated_guide_text)
        st.write(reference_material_text)

        st.subheader("Updated User Guide Content")

        # Generate the updated user guide content using LLM
        updated_guide = generate_text(outdated_guide_text, reference_material_text)

        # Display the generated text on the app
        st.write(updated_guide)

        st.subheader("Download the Updated User Guide")

        # Create .docx file
        with open("updated_guide.docx", "w") as f:
            # Write from generated text
            f.write(updated_guide)

        # Allow app user to download .docx file(updated user guide file) containing generated text
        st.download_button("Download", updated_guide)

    else:
        st.error("Please upload both files.")


if __name__ == '__main__':
    main()
