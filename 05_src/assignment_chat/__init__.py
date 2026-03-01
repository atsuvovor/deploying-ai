import os
from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv(".secrets")

# Ensure CHROMA_OPENAI_API_KEY is set globally
if "CHROMA_OPENAI_API_KEY" not in os.environ:
    os.environ["CHROMA_OPENAI_API_KEY"] = os.getenv("API_GATEWAY_KEY")