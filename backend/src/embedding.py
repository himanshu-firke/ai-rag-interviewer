"""
Embedding — Handles embedding generation for the RAG pipeline.
Uses ChromaDB's built-in default embedding function (all-MiniLM-L6-v2)
which runs locally and is completely free.
"""


def get_embedding_info() -> dict:
    """Get info about the current embedding model."""
    return {
        "model": "all-MiniLM-L6-v2 (ChromaDB default)",
        "type": "local",
        "dimensions": 384,
        "cost": "free",
        "provider": "sentence-transformers via ChromaDB",
    }


# Note: ChromaDB handles embeddings internally when you pass
# `documents` without `embeddings` to collection.add/upsert/query.
# This module exists for documentation and potential future swapping
# to external embedding providers (Gemini, Cohere, OpenAI, etc.)
#
# To switch to an external provider, implement a custom
# chromadb.EmbeddingFunction and pass it to get_or_create_collection().
