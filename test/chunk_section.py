from typing import List, Dict
import re
from docx import Document

class AgenticChunker:
    # process_document function
    def process_document(self, file_path: str):
        # Create document object
        document = Document(file_path)

        # Split document into sections
        sections = self._split_into_sections(document)

        return sections

    def _split_into_sections(self, document: Document) -> List[Dict[str, str]]:
        # Create list of sections
        sections = []
        current_section = {"title": "", "content": []}

        # Iterate through each paragraph in the document
        for paragraph in document.paragraphs:
            # Check if the paragraph string starts with a numbered section
            if re.match(r'^\d+\.', paragraph.text.strip()):
                # If there is an existing current_section, append it to the list of sections
                if current_section["title"]:
                    sections.append(current_section)

                # Create new current_section with new title and new content
                current_section = {"title": paragraph.text.strip(), "content": []}
            # If there is no title, append the paragraph text as the current_section's content
            else:
                current_section["content"].append(paragraph.text)

        if current_section["title"]:
            sections.append(current_section)

        return sections

if __name__ == "__main__":
    ac = AgenticChunker()

    # Process the document
    result = ac.process_document('demo_guide.docx')

    # Print each section
    for section in result:
        print(section)
