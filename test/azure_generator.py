from haystack.components.generators import AzureOpenAIGenerator
from haystack.dataclasses import ChatMessage
import os
from dotenv import load_dotenv

# Environment Variables
load_dotenv()

api_key=os.getenv("AZURE_OPENAI_API_KEY")
endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name=os.getenv("DEPLOYMENT_NAME")

# Azure OpenAI Client
generator = AzureOpenAIGenerator(azure_endpoint=endpoint,
                        api_key=api_key,
                        azure_deployment=deployment_name)

# generator.run(messages=[ChatMessage.from_user("What is the best French cheese?")])
