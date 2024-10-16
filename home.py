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

# Quick Start Guide
st.header("Quick Start Guide")
with st.expander("How to Update a Document"):
    st.markdown("""
    1. Navigate to the Documents section
    2. Upload your document
    3. Provide reference material (e.g., instructions, new text, context)
    4. Review AI-suggested updates
    5. Make any necessary edits
    6. Download your updated document
    """)

with st.expander("How to Create/Update Slides"):
    st.markdown("""
    1. Go to the Slides section
    2. Choose to update existing slides or create new ones
    3. Upload your PowerPoint file (if updating)
    4. Provide reference material for updates or new content
    5. Review AI-generated content
    6. Make any desired modifications
    7. Download your new or updated presentation
    """)

with st.expander("How to Use the Chatbot"):
    st.markdown("""
    1. Navigate to the Chat section
    2. Optionally upload relevant documents for context
    3. Type your question or request
    4. Review the AI's response
    5. Ask follow-up questions as needed
    """)

# FAQs
st.header("Frequently Asked Questions")
faq_data = {
    "What file formats are supported?": "We support .docx, .pdf, and .pptx files.",
    "How accurate is the AI-generated content?": "While highly accurate, always review AI suggestions for your specific needs.",
    "Can I use this for sensitive documents?": "We recommend against uploading sensitive or confidential information.",
    "What should I include in my reference material?": "Include specific instructions, desired changes, new content, or any context that helps explain the updates you need.",
    "How do I report issues or provide feedback?": "Use the 'Contact Support' link in the footer of the application."
}

# Placeholder for Limitations
st.header("Limitations")
st.info("Information about system limitations will be provided here in the future.")
