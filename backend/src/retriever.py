"""
Retriever — Query construction and context retrieval from the vector store.
Builds semantic queries from resume + role and retrieves relevant chunks.
"""

from backend.src.vector_store import query_documents
from backend.src import rag_logger
from backend.config import settings


class RetrievedContext:
    """Represents retrieved context with metadata and confidence scores."""

    def __init__(self, documents: list[str], metadatas: list[dict], distances: list[float]):
        self.documents = documents
        self.metadatas = metadatas
        self.distances = distances

    @property
    def combined_text(self) -> str:
        parts = []
        for doc, meta in zip(self.documents, self.metadatas):
            source = meta.get("source", "Unknown")
            page = meta.get("page", "?")
            parts.append(f"[Source: {source}, Page {page}]\n{doc}")
        return "\n\n---\n\n".join(parts)

    @property
    def sources(self) -> list[dict]:
        seen = set()
        sources = []
        for meta, dist in zip(self.metadatas, self.distances):
            key = f"{meta.get('source', '')}:{meta.get('page', '')}"
            if key not in seen:
                seen.add(key)
                confidence = max(0, round((1 - dist) * 100, 1))
                sources.append({
                    "source": meta.get("source", "Unknown"),
                    "page": meta.get("page", 0),
                    "confidence": confidence,
                })
        return sources

    @property
    def avg_confidence(self) -> float:
        if not self.distances:
            return 0.0
        return round((1 - sum(self.distances) / len(self.distances)) * 100, 1)


# Role-specific base queries
ROLE_QUERIES = {
    "AI/ML Engineer": [
        "machine learning algorithms and model training",
        "neural networks deep learning architectures",
        "feature engineering and data preprocessing",
    ],
    "Backend Engineer": [
        "system design and distributed systems",
        "database design and optimization",
        "API design and microservices architecture",
    ],
    "Data Scientist": [
        "statistical analysis and hypothesis testing",
        "data visualization and exploratory data analysis",
        "machine learning model evaluation and metrics",
    ],
}


def build_queries(
    skills: list[str], technologies: list[str], role: str,
    previous_topics: list[str] = None,
) -> list[str]:
    """Build semantic search queries from resume + role."""
    queries = list(ROLE_QUERIES.get(role, ROLE_QUERIES["AI/ML Engineer"]))

    for skill in skills[:5]:
        queries.append(f"{skill} concepts and applications in {role}")
    for tech in technologies[:3]:
        queries.append(f"{tech} implementation patterns and best practices")

    if previous_topics:
        queries = [q for q in queries if not any(t.lower() in q.lower() for t in previous_topics)]

    # Deduplicate
    seen = set()
    unique = []
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)

    return unique[:10]


def retrieve(
    skills: list[str], technologies: list[str], role: str,
    previous_topics: list[str] = None, top_k: int = None,
) -> RetrievedContext:
    """
    Full retrieval pipeline: build queries -> query vector store -> return context.
    Logs detailed retrieval info to terminal.
    """
    top_k = top_k or settings.TOP_K_RETRIEVAL

    # Build queries
    queries = build_queries(skills, technologies, role, previous_topics)
    rag_logger.log_retrieval_queries(queries)

    # Query vector store (one query at a time for dedup)
    all_docs, all_metas, all_dists = [], [], []
    seen_ids = set()

    for query in queries:
        try:
            results = query_documents(query_texts=[query], n_results=top_k)
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        all_docs.append(results["documents"][0][i])
                        all_metas.append(results["metadatas"][0][i])
                        all_dists.append(results["distances"][0][i])
        except Exception as e:
            print(f"[WARN] Retrieval failed for '{query[:50]}': {e}")

    # Sort by relevance and take top results
    if all_dists:
        combined = sorted(zip(all_dists, all_docs, all_metas), key=lambda x: x[0])
        combined = combined[:top_k * 2]
        all_dists, all_docs, all_metas = zip(*combined)
        all_dists, all_docs, all_metas = list(all_dists), list(all_docs), list(all_metas)

    ctx = RetrievedContext(all_docs, all_metas, all_dists)

    # Log retrieved chunks to terminal
    rag_logger.log_retrieved_chunks(ctx.documents, ctx.metadatas, ctx.distances)
    rag_logger.log_full_context(ctx.combined_text)

    return ctx
