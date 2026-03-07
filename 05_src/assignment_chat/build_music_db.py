#build_music_db.py

import os
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]  # 05_src folder
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".secrets")

api_key = os.getenv("API_GATEWAY_KEY")
if not api_key:
    raise ValueError("API_GATEWAY_KEY not found in environment.")

os.environ["CHROMA_OPENAI_API_KEY"] = api_key

# -----------------------------
# Initialize Chroma client
# -----------------------------
CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"
CHROMA_DB_PATH.mkdir(exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# -----------------------------
# Recreate collection safely
# -----------------------------
COLLECTION_NAME = "music_reviews"

# Delete existing collection if it exists to avoid duplicates
existing_collections = [c.name for c in client.list_collections()]
if COLLECTION_NAME in existing_collections:
    client.delete_collection(COLLECTION_NAME)

collection = client.create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)

# -----------------------------
# Load dataset
# -----------------------------
DATA_FILE = Path(__file__).parent / "music_docs.json"
if not DATA_FILE.exists():
    raise FileNotFoundError(f"{DATA_FILE} not found. Create a small dataset first.")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    docs = json.load(f)

documents = [item["review"] for item in docs]
ids = [item["id"] for item in docs]
metadatas = [
    {
        "artist": item["artist"],
        "title": item["title"],
        "year": item["year"],
        "score": item["score"]
    }
    for item in docs
]

# -----------------------------
# Add documents to collection
# -----------------------------
collection.add(
    documents=documents,
    ids=ids,
    metadatas=metadatas
)

print(" Chroma DB built successfully.")