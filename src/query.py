# src/query.py
import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Dict
import weaviate
from langchain_google_genai import GoogleGenerativeAIEmbeddings,GoogleGenerativeAI

from config import (
    WEAVIATE_URL,
    WEAVIATE_CLASS_NAME,
    TOP_K,
)


def get_weaviate_client() -> weaviate.Client:
    """Return a weaviate client connected to WEAVIATE_URL."""
    return weaviate.Client(WEAVIATE_URL)


def embed_query_with_google(question: str) -> List[float]:
    """
    Use Google Generative AI embeddings to convert the question into a vector.
    Returns a plain Python list of floats suitable for Weaviate's nearVector.
    """
    embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",google_api_key=os.getenv("google_api_key"))
    # embed_documents takes a list and returns a list of vectors
    vecs = embedder.embed_documents([question])
    if not vecs or len(vecs) == 0:
        raise RuntimeError("Embedding API returned no vector.")
    return vecs[0]


def retrieve_context(question: str) -> List[Dict]:
    """
    Embed the question using Google embeddings and query Weaviate for top-K chunks.
    Returns the list of objects (dictionaries) from Weaviate.
    """
    client = get_weaviate_client()

    query_vec = embed_query_with_google(question)

    # Query Weaviate using nearVector and return top-K results
    result = (
        client.query
        .get(WEAVIATE_CLASS_NAME, ["text", "source", "chunk_id"])
        .with_near_vector({"vector": query_vec})
        .with_limit(TOP_K)
        .do()
    )

    # Defensive checks for response shape
    get_block = result.get("data", {}).get("Get", {})
    if not get_block:
        return []

    return get_block.get(WEAVIATE_CLASS_NAME, [])

def generate_answer_with_google(question: str, context_chunks: List[Dict]) -> str:
    model=GoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("google_api_key")
    )
    prompt = (
        "You are an assistant. Use the provided CONTEXT to answer the question. "
        "If the answer is not contained, say you don't know.\n\n"
        f"CONTEXT:\n{chr(10).join(context_chunks)}\n\nQUESTION: {question}"
    )
    resp = model.generate(prompts=[prompt])
    return resp.content if hasattr(resp, "content") else str(resp)
    
def simple_print_answer(question: str):
    hits = retrieve_context(question)

    print("\n=== Question ===")
    print(question)
    print("\n=== Retrieved Chunks (for context) ===")
    if not hits:
        print("[NO HITS] No relevant chunks found.")
        return

    for i, hit in enumerate(hits, 1):
        src = hit.get("source", "unknown")
        cid = hit.get("chunk_id", "n/a")
        text = hit.get("text", "")
        print(f"\n--- Chunk {i} (source={src}, id={cid}) ---")
        print(text[:1000] + ("..." if len(text) > 1000 else ""))

    print("\n[NOTE] In Sprint 2 we’ll send these chunks to an LLM to generate a proper answer.")
def retrive_and_answer(question: str ,top_k :int = TOP_K) -> str:
    hits = retrieve_context(question)

    if not hits:
        return "No relevant chunks found."

    context_texts = [hit.get("text", "") for hit in hits]
    answer = generate_answer_with_google(question, context_texts)
    return answer

