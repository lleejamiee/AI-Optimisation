from openai import OpenAI
import streamlit as st

# Initialize OpenAI client with local inference server (LM Studio)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Prompt for LLM
prompt = """
You are a technical writer tasked with creating a user guide for a product/service. 
Your task is to create a user guide by incorporating relevant information from the provided outdated user guide.
Only generate the content that is to be used in this new user guide.
Do not provide explanations or notes.

The user will input one text document
Document 1: Outdated User Guide
"""

# llm on local inference server(LM Studio)
def generate_text(outdated_guide):
    history = [
        {"role": "system",
         "content": prompt},
        {"role": "user",
         "content": f"Outdated User Guide:\n{outdated_guide}"}
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

def main():
    st.set_page_config(page_title="User Guide Creator")

    # Set app header
    st.header("Create a user guide")

    # Upload both outdated user guide and reference material
    outdated_guide_file = st.file_uploader("Choose the outdated user guide .txt file...", type="txt") # Can also use doc type

    if outdated_guide_file is not None:
        # Read the contents of both files
        outdated_guide = outdated_guide_file.read().decode("utf-8")

        # Uncomment to display the contents of each .txt file on the app
        #st.write(outdated_guide)

        st.subheader("Updated User Guide Content")

        # Generate the updated user guide content using LLM
        updated_guide = generate_text(outdated_guide)

        # Display the generated text on the app
        st.write(updated_guide)

        st.subheader("Download the Updated User Guide")

        # Create .txt file
        with open("new_guide.txt", "w") as f:
            # Write from generated text
            f.write(updated_guide)

        # Allow app user to download .txt file(updated user guide file) containing generated text
        st.download_button("Download", updated_guide)

    else:
        st.error("Please upload outdate file.")

if __name__ == '__main__':
    main()
