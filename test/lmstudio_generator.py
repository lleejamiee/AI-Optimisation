from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
import os

# Initialize the OpenAIChatGenerator with your local LLM API details
os.environ["OPENAI_API_KEY"]="lm-studio"  # Replace with your actual API key
generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("OPENAI_API_KEY"),
    api_base_url="http://localhost:1234/v1",  # URL of your local LLM server
    model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"  # Model identifier
)

generator.run(messages=[ChatMessage.from_user("What is the best French cheese?")])