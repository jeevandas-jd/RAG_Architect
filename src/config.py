# src/config.py

WEAVIATE_URL = "http://localhost:8080"

# We disable Weaviate's own vectorizer and push our own embeddings
WEAVIATE_CLASS_NAME = "DocumentChunk"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5
