import time
import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
from app.data.triage_guidelines import TRIAGE_GUIDELINES

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="app/chroma_data")
collection = chroma_client.get_or_create_collection(name="triage_guidelines")


def get_embedding(text: str, max_retries: int = 3) -> list:
    for attempt in range(max_retries):
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except ResourceExhausted:
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 15)
            else:
                raise


def populate_guidelines():
    collection_count = collection.count()
    existing_ids = set()
    if collection_count > 0:
        existing_ids = set(collection.get()["ids"])

    added = 0
    for guideline in TRIAGE_GUIDELINES:
        if guideline["id"] in existing_ids:
            continue
        embedding = get_embedding(guideline["text"])
        collection.add(
            ids=[guideline["id"]],
            embeddings=[embedding],
            documents=[guideline["text"]]
        )
        added += 1

    return f"Added {added} new guidelines. Total in store: {collection.count()}."


def search_guidelines(query_text: str, n_results: int = 3) -> list:
    query_embedding = None
    for attempt in range(3):
        try:
            query_embedding = genai.embed_content(
                model="models/gemini-embedding-001",
                content=query_text,
                task_type="retrieval_query"
            )["embedding"]
            break
        except ResourceExhausted:
            if attempt < 2:
                time.sleep((attempt + 1) * 15)
            else:
                return []

    if query_embedding is None:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    ids = results["ids"][0]
    documents = results["documents"][0]
    return [{"id": ids[i], "text": documents[i]} for i in range(len(documents))]