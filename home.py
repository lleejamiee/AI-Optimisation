import streamlit as st

st.set_page_config(page_title="Home", layout="wide")
# st.header("Select an option")
#
# st.page_link("pages/document.py", label="Document")
# st.page_link("pages/slide.py", label="Slide")
# st.page_link("pages/video.py", label="Video")
# st.page_link("pages/chatbot.py", label="Chat")


st.title("Prototype Tool Application")

st.markdown("""
This application helps you update, create, and maintain documents efficiently using AI-powered tools.
""")

# Navigation Guide
st.header("Navigation Guide")
st.markdown("""
- **Documents**: Update and create text-based documents
- **Slides**: Work with PowerPoint presentations
- **Chat**: Interact with our AI assistant
""")


# Reference Material Explanation
st.header("Understanding Reference Material")

st.markdown("""
Reference material is the information or context you provide to update a document or create new content. This can include:
- Instructions for changes
- Direct text to replace existing content
- New information to be incorporated
- Context about desired updates

The AI uses this reference material to understand your needs and generate appropriate updates or new content. For the best results:
- Prepare clear, well-structured reference material for best results
- Be specific in your instructions and desired changes
- Provide section header for updates if possible
""")
