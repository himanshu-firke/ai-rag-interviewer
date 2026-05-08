"""
Knowledge ingestion service.
Uses src/ modules for data loading, chunking, and vector storage.
"""

from backend.src.data_loader import extract_pages_from_pdf, find_pdf_files
from backend.src.chunker import chunk_text
from backend.src.vector_store import generate_chunk_id, upsert_documents, get_collection_stats
from backend.config import settings


def ingest_knowledge_base(role: str = None) -> dict:
    """Ingest all PDF documents from the knowledge base directory."""
    pdf_files = find_pdf_files(settings.KNOWLEDGE_BASE_PATH)
    if not pdf_files:
        return {"error": "No PDF files found in knowledge base"}

    print(f"[INFO] Found {len(pdf_files)} PDF files to ingest")

    total_chunks = 0
    total_pages = 0
    processed_files = []

    for pdf_path in pdf_files:
        filename = pdf_path.name
        print(f"[INFO] Processing: {filename}")

        try:
            pages = extract_pages_from_pdf(str(pdf_path))
            total_pages += len(pages)

            all_chunks, all_metadatas, all_ids = [], [], []

            for page_data in pages:
                chunks = chunk_text(page_data["text"])
                for idx, chunk in enumerate(chunks):
                    if len(chunk.strip()) < 50:
                        continue
                    chunk_id = generate_chunk_id(chunk, filename, page_data["page_num"])
                    all_chunks.append(chunk)
                    all_metadatas.append({
                        "source": filename, "page": page_data["page_num"],
                        "chunk_index": idx, "role": role or "general",
                    })
                    all_ids.append(chunk_id)

            if all_chunks:
                count = upsert_documents(all_chunks, all_metadatas, all_ids)
                total_chunks += count
                processed_files.append(filename)
                print(f"  [OK] {filename}: {count} chunks stored")

        except Exception as e:
            print(f"  [ERR] Error processing {filename}: {e}")

    stats = get_collection_stats()
    result = {
        "files_processed": len(processed_files),
        "file_names": processed_files,
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "collection_count": stats["count"],
    }
    print(f"\n[INFO] Ingestion Complete: {result}")
    return result
