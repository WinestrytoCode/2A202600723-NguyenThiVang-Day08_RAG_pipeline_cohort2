"""
Task 4 — Chunking & Indexing vào Vector Store (Qdrant).

Pipeline: load markdown (data/standardized/) → chunk → embed (bge-m3) → index (Qdrant).

Lựa chọn & lý do:
    - Chunking: RecursiveCharacterTextSplitter. Văn bản luật ở đây là text thuần
      (heading "Điều N." KHÔNG phải markdown #) nên recursive theo ký tự + separator
      tiếng Việt là phù hợp; chunk_size=800 ký tự (~200 token, đủ gọn 1 khoản/điều),
      overlap=120 (~15%) để không cắt mất ngữ cảnh ở ranh giới.
    - Embedding: BAAI/bge-m3 (1024-dim, multilingual, tốt cho tiếng Việt), chạy local.
      normalize_embeddings=True để khớp Distance.COSINE của Qdrant.
    - Vector store: Qdrant embedded (path=./qdrant_data) — không cần Docker, persist ra đĩa.

Chạy:
    python -m src.task4_chunking_indexing
"""

from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
QDRANT_PATH = str(Path(__file__).parent.parent / "qdrant_data")


# =============================================================================
# CONFIGURATION
# =============================================================================

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

VECTOR_STORE = "qdrant"
COLLECTION_NAME = "DrugLawDocs"

# Separator ưu tiên cho tiếng Việt (đoạn → câu → mệnh đề → từ → ký tự).
VI_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]


# =============================================================================
# MODEL (load 1 lần, tái sử dụng cho Task 5)
# =============================================================================

_model = None


def get_model():
    """Trả về SentenceTransformer bge-m3 (lazy load, cache module-level)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed danh sách text bằng bge-m3 (normalize cho cosine)."""
    embs = get_model().encode(
        texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True
    )
    return embs.tolist()


# =============================================================================
# IMPLEMENTATION
# =============================================================================

def load_documents() -> list[dict]:
    """Đọc toàn bộ markdown từ data/standardized/. Trả list {content, metadata}."""
    documents = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in md_file.parts else "news"
        documents.append({
            "content": content,
            "metadata": {"source": md_file.name, "type": doc_type},
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chunk theo RecursiveCharacterTextSplitter. chunk_index gán theo từng tài liệu."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=VI_SEPARATORS,
        length_function=len,
    )
    chunks = []
    for doc in documents:
        for i, piece in enumerate(splitter.split_text(doc["content"])):
            if not piece.strip():
                continue
            chunks.append({
                "content": piece,
                "metadata": {**doc["metadata"], "chunk_index": i},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm key 'embedding' (1024 float) cho mỗi chunk."""
    vectors = embed_texts([c["content"] for c in chunks])
    for chunk, vec in zip(chunks, vectors):
        chunk["embedding"] = vec
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> int:
    """Tạo lại collection và upsert chunks vào Qdrant. Trả số điểm đã index."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    client = QdrantClient(path=QDRANT_PATH)
    try:
        # Re-index sạch: xoá collection cũ nếu có rồi tạo mới.
        if client.collection_exists(COLLECTION_NAME):
            client.delete_collection(COLLECTION_NAME)
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )

        points = [
            PointStruct(
                id=i,
                vector=chunk["embedding"],
                payload={
                    "content": chunk["content"],
                    "source": chunk["metadata"]["source"],
                    "type": chunk["metadata"]["type"],
                    "chunk_index": chunk["metadata"]["chunk_index"],
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        for j in range(0, len(points), 256):  # upsert theo lô
            client.upsert(COLLECTION_NAME, points=points[j:j + 256], wait=True)

        return client.count(COLLECTION_NAME).count
    finally:
        client.close()  # nhả lock thư mục embedded


def run_pipeline():
    """Chạy toàn bộ: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE} @ {QDRANT_PATH}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    n = index_to_vectorstore(chunks)
    print(f"✓ Indexed {n} points to collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    run_pipeline()
