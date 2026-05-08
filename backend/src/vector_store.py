"""
Vector Store — ChromaDB operations for storing and querying document chunks.
Provides a clean interface for the RAG pipeline to interact with the vector DB.
"""

import hashlib
from pathlib import Path
import chromadb
from backend.config import settings


_client = None
_collection = None


def get_client() -> chromadb.PersistentClient:
    """Get or create a ChromaDB persistent client (singleton)."""
    global _client
    if _client is None:
        chroma_path = Path(settings.CHROMA_PATH)
        chroma_path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(chroma_path))
    return _client


def get_collection(name: str = "knowledge_base"):
    """Get or create a ChromaDB collection."""
    global _collection
    if _collection is None or _collection.name != name:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def generate_chunk_id(text: str, source: str, page: int) -> str:
    """Generate a deterministic ID for deduplication."""
    content = f"{source}:{page}:{text[:200]}"
    return hashlib.md5(content.encode()).hexdigest()


def upsert_documents(
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
    collection_name: str = "knowledge_base",
    batch_size: int = 100,
) -> int:
    """
    Upsert documents into ChromaDB. ChromaDB generates embeddings automatically.

    Returns:
        Number of documents upserted.
    """
    collection = get_collection(collection_name)
    count = 0

    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        collection.upsert(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end],
        )
        count += end - i

    return count


def query_documents(
    query_texts: list[str],
    n_results: int = 5,
    where_filter: dict = None,
    collection_name: str = "knowledge_base",
) -> dict:
    """
    Query the vector store with text queries.
    ChromaDB embeds the queries automatically using its default model.

    Returns:
        ChromaDB query results dict with ids, documents, metadatas, distances.
    """
    collection = get_collection(collection_name)

    if collection.count() == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    params = {
        "query_texts": query_texts,
        "n_results": min(n_results, collection.count()),
    }

    if where_filter:
        params["where"] = where_filter

    return collection.query(**params)


def get_collection_stats() -> dict:
    """Get stats about the current collection."""
    collection = get_collection()
    return {
        "name": collection.name,
        "count": collection.count(),
        "metadata": collection.metadata,
    }
