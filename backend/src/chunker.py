"""
Chunker — Text chunking strategies for the RAG pipeline.
Implements paragraph-aware chunking with configurable overlap.
"""

from backend.config import settings


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> list[str]:
    """
    Split text into overlapping chunks at paragraph boundaries.
    Preserves semantic context by respecting paragraph structure.

    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk (default from settings)
        chunk_overlap: Characters of overlap between chunks

    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk += ("\n\n" + para if current_chunk else para)
        else:
            if current_chunk:
                chunks.append(current_chunk)

            # Handle paragraphs longer than chunk_size
            if len(para) > chunk_size:
                words = para.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= chunk_size:
                        current_chunk += (" " + word if current_chunk else word)
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = word
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    # Add overlap between chunks for context continuity
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            overlap_text = chunks[i - 1][-chunk_overlap:]
            overlapped.append(overlap_text + "\n" + chunks[i])
        return overlapped

    return chunks


def get_chunk_stats(chunks: list[str]) -> dict:
    """Get statistics about the chunks."""
    if not chunks:
        return {"count": 0, "avg_length": 0, "min_length": 0, "max_length": 0}
    lengths = [len(c) for c in chunks]
    return {
        "count": len(chunks),
        "avg_length": round(sum(lengths) / len(lengths)),
        "min_length": min(lengths),
        "max_length": max(lengths),
    }
