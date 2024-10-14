from docx import Document
import re
import tempfile
import os


def temp_file(uploaded_file):
    if uploaded_file is not None:
        # Create a temporary file with the same extension as the uploaded file
        file_extension = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    return


def check_title(paragraph):
    return bool(re.match(r'^\d+(?:\.\d+)*\s+.+$', paragraph.text.strip()))


def update_document(original_file_path, updated_sections):
    doc = Document(original_file_path)

    # Create a mapping of section titles to updated content
    content_map = {section['original_content'].split('\n', 1)[0].strip(): section['updated_content'].strip()
                   for section in updated_sections}

    current_section = None
    update_in_progress = False

    for para in doc.paragraphs:
        if check_title(para):
            # This paragraph is a section title
            current_section = para.text.strip()
            if current_section in content_map:
                update_in_progress = True
                # Update the title if it has changed
                new_content_lines = content_map[current_section].split('\n')
                new_title = new_content_lines[0].strip()
                if new_title != current_section:
                    para.text = new_title
                # Prepare the content for updating
                remaining_content = '\n'.join(new_content_lines[1:]).strip()
                content_lines = remaining_content.split('\n')
                content_index = 0
            else:
                update_in_progress = False
        elif update_in_progress:
            # This paragraph is part of a section we're updating
            if content_index < len(content_lines):
                # Update the paragraph text
                para.text = content_lines[content_index]
                content_index += 1

                # Apply bullet point formatting if necessary
                if para.text.strip().startswith(('•', '-', '*')):
                    para.style = 'List Bullet'
                else:
                    para.style = 'Normal'
            else:
                # Reach end of new content
                update_in_progress = False
                # Clear remaining paragraphs in this section
                para.text = ""

    # Save the updated document
    updated_file_path = original_file_path.rsplit('.', 1)[0] + '_updated.docx'
    doc.save(updated_file_path)
    return updated_file_path


def prepare_updated_document(original_file_path, updated_sections):
    updated_file_path = update_document(original_file_path, updated_sections)

    # Read the updated file
    with open(updated_file_path, "rb") as file:
        file_data = file.read()

    # Get the filename
    filename = os.path.basename(updated_file_path)

    # Clean up the temporary file
    os.remove(updated_file_path)

    return file_data, filename
