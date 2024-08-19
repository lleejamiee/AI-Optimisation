import os
import json
from pptx.util import Pt
from pptx import Presentation
from openai import AzureOpenAI


class SlideProcessor:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-06-01"
    )

    query_json = """{
        "input_text": "[[content]]",
        "output_format": "json",
        "json_structure": {
        "generated_slides": "{{presentation_slides}}"
        }
    }"""

    system_prompt = """
    You are a helpful technical writer tasked with updating an outdated user guide for a product/service. 
    The user will input the following documents
    Document 1: Outdated User Guide
    Document 2: Reference Material
    Based on the input documents, your task is to update an outdated user guide slides by incorporating relevant information from the provided reference material. Generate only the JSON data required by the user and nothing else.
    Do not include any additional text or explanations. Each slide should have a {{header}}, {{content}}. Return only the JSON data as specified below.
    """
    prompt = query_json.replace("[[content]]", system_prompt)

    def extract_formatting(slide):
        formatting_info = []
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        formatting_info.append({
                            "text": run.text,
                            "font_size": run.font.size.pt if run.font.size else None,
                            "font_bold": run.font.bold,
                            "font_italic": run.font.italic,
                            "font_name": run.font.name,
                            "font_color": run.font.color.rgb if run.font.color else None,
                        })
        return formatting_info

    def generate_presentation(outdated_guide, reference_material):
        completion = SlideProcessor.client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": SlideProcessor.system_prompt},
                {
                    "role": "user",
                    "content": f"Outdated User Guide:\n{outdated_guide}\n\nReference Material:\n{reference_material}",
                },
            ]
        )

        response_content = completion.choices[0].message.content
        # json_rsp = json.loads(response_content)
        # slide_data = json_rsp.get("generated_slides")

        return response_content

    def create_slides(slide_data, formatting_info):
        prs = Presentation()

        for slide, formatting in zip(slide_data, formatting_info):
            slide_layout = prs.slide_layouts[1]
            new_slide = prs.slides.add_slide(slide_layout)

            if slide['header']:
                title = new_slide.shapes.title
                title.text = slide['header']

            if slide['content']:
                body_shape = new_slide.shapes.placeholders[1]
                text_frame = body_shape.text_frame

                for content, format_info in zip(slide['content'], formatting):
                    p = text_frame.add_paragraph()
                    run = p.add_run()
                    run.text = content

                    if format_info.get('font_size'):
                        run.font.size = Pt(format_info['font_size'])
                    if format_info.get('font_bold'):
                        run.font.bold = format_info['font_bold']
                    if format_info.get('font_italic'):
                        run.font.italic = format_info['font_italic']
                    if format_info.get('font_name'):
                        run.font.name = format_info['font_name']
                    if format_info.get('font_color'):
                        run.font.color.rgb = format_info['font_color']


    def extract_pptx_to_json(file):
        presentation = Presentation(file)
        slides_data = []

        for slide_number, slide in enumerate(presentation.slides):
            slide_content = {
                "slide_number": slide_number + 1,
                "shapes": []
            }

            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_content["shapes"].append({"text": shape.text})

            slides_data.append(slide_content)

        json_data = json.dumps((slides_data), indent=4)
        return json_data