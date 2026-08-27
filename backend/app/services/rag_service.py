import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.data.triage_guidelines import TRIAGE_GUIDELINES

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="app/chroma_data")

collection = chroma_client.get_or_create_collection(name="triage_guidelines")


def get_embedding(text: str) -> list:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]


def populate_guidelines():
    existing = collection.count()
    if existing > 0:
        return f"Already populated with {existing} guidelines, skipping."

    for guideline in TRIAGE_GUIDELINES:
        embedding = get_embedding(guideline["text"])
        collection.add(
            ids=[guideline["id"]],
            embeddings=[embedding],
            documents=[guideline["text"]]
        )

    return f"Populated {len(TRIAGE_GUIDELINES)} guidelines."


def search_guidelines(query_text: str, n_results: int = 2) -> list:
    query_embedding = genai.embed_content(
        model="models/gemini-embedding-001",
        content=query_text,
        task_type="retrieval_query"
    )["embedding"]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0] if results["documents"] else []