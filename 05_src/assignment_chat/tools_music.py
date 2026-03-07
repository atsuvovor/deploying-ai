# tools_music.py
from langchain.tools import tool
from pydantic import BaseModel, Field
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pathlib import Path

# -----------------------------
# Load environment variables
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".secrets")

# -----------------------------
# Initialize Chroma client
# -----------------------------
client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="music_reviews",
    embedding_function=embedding_function
)

# -----------------------------
# Data model
# -----------------------------
class MusicReviewData(BaseModel):
    title: str
    artist: str
    review: str
    score: float

# -----------------------------
# Tool function
# -----------------------------
@tool
def recommend_albums(query: str, n_results: int = 1) -> list[MusicReviewData]:
    """
    Loads environment variables from .env and .secrets.
    Uses SentenceTransformerEmbeddingFunction → no OpenAI key needed.
    recommend_albums  returns MusicReviewData objects.
    Collection name is music_reviews.
    """
    results = collection.query(query_texts=[query], n_results=n_results)

    recommendations = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        review_text = results["documents"][0][i]

        rec = MusicReviewData(
            title=metadata["title"],
            artist=metadata["artist"],
            review=review_text,
            score=metadata["score"]
        )
        recommendations.append(rec)

    return recommendations