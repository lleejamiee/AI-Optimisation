from langchain_core.prompts import ChatPromptTemplate
import uuid
from langchain_groq import ChatGroq
import os
from typing import List, Dict
from dotenv import load_dotenv
import re
from docx import Document

load_dotenv()

class AgenticChunker:
    def __init__(self, groq_api_key=None):
        self.chunks = {}
        self.id_truncate_limit = 5

        if groq_api_key is None:
            groq_api_key = os.getenv("GROQ_API_KEY")

        if groq_api_key is None:
            raise ValueError("API key is not provided and not found in environment variables")

        self.llm = ChatGroq(model='llama3-8b-8192', groq_api_key=groq_api_key, temperature=0)

    def process_document(self, file_path: str):
        document = Document(file_path)
        sections = self._split_into_sections(document)
        for section in sections:
            self._process_section(section)

    def _split_into_sections(self, document: Document) -> List[Dict[str, str]]:
        sections = []
        current_section = {"title": "", "content": []}

        for paragraph in document.paragraphs:
            if re.match(r'^\d+\.', paragraph.text.strip()):
                if current_section["title"]:
                    sections.append(current_section)
                current_section = {"title": paragraph.text.strip(), "content": []}
            else:
                current_section["content"].append(paragraph.text)

        if current_section["title"]:
            sections.append(current_section)

        return sections

    def _process_section(self, section: Dict[str, str]):
        title = section["title"]
        content = "\n".join(section["content"]).strip()

        chunk_id = str(uuid.uuid4())[:self.id_truncate_limit]
        self.chunks[chunk_id] = {
            'chunk_id': chunk_id,
            'title': title,
            'content': content,
            'summary': self._generate_summary(content),
            'chunk_index': len(self.chunks)
        }

    def _generate_summary(self, content: str) -> str:
        PROMPT = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are an AI assistant tasked with summarizing sections of a training guide.
                Provide a brief, one-sentence summary of the main point or purpose of the given section.
                """
            ),
            ("user", "Summarize the following section:\n{content}")
        ])

        runnable = PROMPT | self.llm
        summary = runnable.invoke({"content": content}).content
        return summary.strip()

    def _find_relevant_chunk(self, query: str) -> str:
        PROMPT = ChatPromptTemplate.from_messages([
            (
                """
                You are an AI assistant helping to find the most relevant section of a training guide based on a user's query.
                You will be provided with summaries of different sections and a user's query.
                Your task is to determine which section is most relevant to the query.

                Each section (chunk) has the following format:
                chunk_id: [unique identifier]
                title: [section title]
                summary: [brief summary of the section]

                Review the provided sections and the user's query carefully.
                If you find a relevant section, return ONLY the chunk_id of the most relevant section, without any additional text or formatting.
                If no section is relevant to the query, return ONLY "No chunks".

                Remember, return ONLY the chunk_id or "No chunks" without any additional explanation.
                """
            ),
            ("user", "Sections:\n{sections}\n\nQuery: {query}\n\nMost relevant chunk_id:")
        ])

        sections = "\n".join(
            [f"chunk_id: {chunk['chunk_id']}, title: {chunk['title']}, summary: {chunk['summary']}" for chunk in
             self.chunks.values()])

        runnable = PROMPT | self.llm
        response = runnable.invoke({"sections": sections, "query": query}).content
        return response.strip()

    def get_relevant_content(self, query: str) -> Dict[str, str]:
        chunk_id = self._find_relevant_chunk(query)
        # Check if the chunk_id given in the response matches a chunk_id in chunks
        if chunk_id in self.chunks:
            return {
                'title': self.chunks[chunk_id]['title'],
                'content': self.chunks[chunk_id]['content']
            }
        else:
            return {'title': 'No relevant section found', 'content': ''}

    def pretty_print_chunks(self):
        print(f"\nYou have {len(self.chunks)} chunks\n")
        for chunk_id, chunk in self.chunks.items():
            print(f"Chunk #{chunk['chunk_index']}")
            print(f"Chunk ID: {chunk_id}")
            print(f"Title: {chunk['title']}")
            print(f"Summary: {chunk['summary']}")
            print("\n")


if __name__ == "__main__":
    ac = AgenticChunker()

    # Sample usage
    ac.process_document('demo_guide.docx')
    ac.pretty_print_chunks()

    # Search text (query)
    query = "What are the core ICT competencies?"

    # query = "Replace the emphasis on older SDLC practices with DevOps and CI/CD pipeline methodologies that are more relevant for today's technology environment."
    # query = "older SDLC practices", "DevOps", "CI/CD pipeline methodologies", "modern technology environment"

    relevant_content = ac.get_relevant_content(query)
    print(f"Query: {query}")
    print(f"Relevant section: {relevant_content['title']}")
    print(f"Content: {relevant_content['content'][:200]}...")