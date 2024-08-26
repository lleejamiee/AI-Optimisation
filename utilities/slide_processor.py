import os
import json
from groq import Groq
from haystack import Pipeline
from haystack import Document
from haystack.components.builders import PromptBuilder
from haystack.utils import Secret
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from pptx.util import Pt
from utilities.prompts import *
from pptx import Presentation
from openai import AzureOpenAI
from dotenv import load_dotenv
from pptx.dml.color import RGBColor, _NoneColor

load_dotenv()

class SlideProcessor:

    # client = AzureOpenAI(
    #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #     api_version="2024-06-01"
    # )

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    query_json = """{
        "input_text": "[[content]]",
        "output_format": "json",
        "json_structure": {
        "generated_slides": [{"header": {header_content}, "content": {content}}]
    }"""

    system_prompt = """
    You are a helpful technical writer tasked with updating an outdated user guide for a product/service. 
    The user will input the following documents
    Document 1: Outdated User Guide
    Document 2: Reference Material
    Based on the input documents, your task is to update an outdated user guide slides by incorporating relevant information from the provided reference material. Generate only the JSON data required by the user and nothing else.
    Do not include any additional text or explanations. Each slide should only have a {{header}}, {{content}} and wrapped in list name generated_slides. Return only the JSON data as specified below. Do not include any additional text or explanations. 
    """
    prompt = query_json.replace("[[content]]", system_prompt)

    # TODO: Need to fix the code so _NoneColor error for font colour goes away
    def extract_formatting(slide):
        formatting_info = []
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        font_color_rgb = RGBColor(0, 0, 0)

                        if run.font.color.rgb is not isinstance(run.font.color.rgb, _NoneColor):
                            font_color_rgb = run.font.color.rgb

                        formatting_info.append({
                            "text": run.text,
                            "font_size": run.font.size.pt if run.font.size else None,
                            "font_bold": run.font.bold,
                            "font_italic": run.font.italic,
                            "font_name": run.font.name,
                            "font_color": font_color_rgb,
                        })
        return formatting_info

    def generate_presentation_content(outdated_guide, reference_material):
        outdated_document = Document(content=outdated_guide)
        reference_document = Document(content=reference_material)
        docstore = InMemoryDocumentStore()
        docstore.write_documents([Document(content=outdated_document.content), Document(content=reference_document.content)])

        template = slides_template
        query = slides_query

        llm = OpenAIGenerator(api_key=Secret.from_env_var("GROQ_OPENAI_API_KEY"), api_base_url="https://api.groq.com/openai/v1", model=os.getenv("GROQ_MODEL_NAME"), generation_kwargs={"temperature": 0.2})

        pipe = Pipeline()
        pipe.add_component("retriever", InMemoryBM25Retriever(document_store=docstore))
        pipe.add_component("prompt_builder", PromptBuilder(template=template))
        pipe.add_component("llm", llm)
        pipe.connect("retriever", "prompt_builder.documents")
        pipe.connect("prompt_builder", "llm")

        res = pipe.run({"retriever": {"query": query}, "prompt_builder": {"query": query}})


        # completion = SlideProcessor.client.chat.completions.create(
        #     model=os.getenv("GROQ_MODEL_NAME"),
        #     messages=[
        #         {"role": "system", "content": SlideProcessor.system_prompt},
        #         {
        #             "role": "user",
        #             "content": f"Outdated User Guide:\n{outdated_guide}\n\nReference Material:\n{reference_material}",
        #         },
        #     ]
        # )

        # response_content = completion.choices[0].message.content

        # Returns the LLM generated response
        return res['llm']['replies'][0]

    # TODO: Change so the original formatting is kept
    @staticmethod
    def create_slides(response_content):
        prs = Presentation()

        json_rsp = json.loads(response_content)
        slide_data = json_rsp.get("generated_slides")
        print(slide_data)

        for slide in slide_data:
            slide_layout = prs.slide_layouts[1]
            new_slide = prs.slides.add_slide(slide_layout)

            if slide['header']:
                title = new_slide.shapes.title
                title.text = slide['header']

            if slide['content']:
                shapes = new_slide.shapes
                body_shape = shapes.placeholders[1]
                tf = body_shape.text_frame

                content = slide['content']
                if isinstance(content, list):
                    content = " ".join(content)

                p = tf.add_paragraph()
                run = p.add_run()
                run.text = content
                run.font.size = Pt(18)
                run.font.bold = True
                run.font.name = "Calibri"

        return prs

    # May not need this
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