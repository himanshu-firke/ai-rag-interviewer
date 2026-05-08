"""
RAG Pipeline Source Module.
Separated into individual components for modularity:
- data_loader: PDF loading and text extraction
- chunker: Text chunking strategies
- embedding: Embedding generation
- vector_store: ChromaDB operations
- retriever: Query construction and retrieval
- llm_client: LLM provider abstraction
- rag_logger: Rich terminal logging
"""

from backend.src.rag_logger import get_logger

logger = get_logger()
