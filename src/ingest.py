# src/ingest.py
import os
import sys
from typing import List
from dotenv import load_dotenv
import weaviate
from tqdm import tqdm
from langchain_google_genai import GoogleGenerativeAIEmbeddings
load_dotenv()
# your existing helpers
from config import (
    WEAVIATE_URL,
    WEAVIATE_CLASS_NAME,
    EMBEDDING_MODEL_NAME,   # not used but okay to keep
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from extractText import extract_text_from_pdf
from TextChunk import text_chunker


def ensure_schema(client: weaviate.Client):
    """
    Ensure the class schema exists in Weaviate. If it does not exist, create it.
    """
    schema = client.schema.get()
    existing_classes = {c["class"] for c in schema.get("classes", [])}
    if WEAVIATE_CLASS_NAME in existing_classes:
        print("[INFO] Schema already exists.")
        return

    class_obj = {
        "class": WEAVIATE_CLASS_NAME,
        "vectorizer": "none",  # we will provide vectors ourselves
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "source", "dataType": ["string"]},
            {"name": "chunk_id", "dataType": ["int"]},
        ],
    }
    client.schema.create_class(class_obj)
    print(f"[INFO] Created class '{WEAVIATE_CLASS_NAME}' in Weaviate.")


def ingest_pdf_to_weaviate(pdf_path: str, source_name: str = None, batch_size: int = 64):
    """
    Ingest PDF -> chunk -> embed (Google) -> push to Weaviate
    """
    if source_name is None:
        source_name = os.path.basename(pdf_path)

    print(f"[INFO] Connecting to Weaviate at {WEAVIATE_URL}")
    client = weaviate.Client(WEAVIATE_URL)

    ensure_schema(client)

    print(f"[INFO] Extracting text from: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text or not text.strip():
        raise ValueError(f"No text extracted from '{pdf_path}'")

    print("[INFO] Chunking text...")
    chunks = text_chunker(text, CHUNK_SIZE, CHUNK_OVERLAP)
    chunks = [c for c in chunks if c and c.strip()]
    print(f"[INFO] Created {len(chunks)} chunks.")

    # Create embeddings via Google API (LangChain wrapper)
    print("[INFO] Creating embeddings using GoogleGenerativeAIEmbeddings...")
    # You can pass model name here if you want; default in your config was kept for parity
    embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",google_api_key=os.getenv("google_api_key"))

    # embed_documents accepts a list of strings and returns List[List[float]]
    all_vectors = []
    # Do batching to avoid huge single requests and to reduce chance of timeouts
    for i in range(0, len(chunks), batch_size):
        batch_texts = chunks[i : i + batch_size]
        try:
            batch_vectors = embedder.embed_documents(batch_texts)
            all_vectors.extend(batch_vectors)
            print(f"[INFO] Embedded batch {i//batch_size + 1} ({len(batch_texts)} items).")
        except Exception as e:
            print(f"[ERROR] Embedding batch starting at {i}: {e}")
            raise

    if len(all_vectors) != len(chunks):
        raise RuntimeError("Mismatch between number of chunks and returned embeddings.")

    # Upload to Weaviate — use batching for efficiency
    print("[INFO] Uploading objects to Weaviate (batched)...")
    with client.batch as batch:
        batch.batch_size = batch_size
        for idx, (chunk_text, vector) in enumerate(tqdm(zip(chunks, all_vectors), total=len(chunks))):
            data_obj = {
                "text": chunk_text,
                "source": source_name,
                "chunk_id": idx,
            }
            # add_data_object will add with the provided vector
            batch.add_data_object(data_obj, WEAVIATE_CLASS_NAME, vector=vector)
    print("[DONE] Ingestion complete.")


"""if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest a PDF into Weaviate using Google embeddings.")
    parser.add_argument("pdf_path", help="Path to the PDF to ingest")
    parser.add_argument("--source", help="Source name for metadata (defaults to filename)", default=None)
    parser.add_argument("--batch-size", type=int, help="Batch size for embeddings and uploads", default=64)
    args = parser.parse_args()

    ingest_pdf_to_weaviate(args.pdf_path, source_name=args.source, batch_size=args.batch_size)
"""