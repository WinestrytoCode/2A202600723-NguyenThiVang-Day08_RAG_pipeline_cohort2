"""
Task 10 — Generation Có Citation.

retrieve (T9) → reorder (chống "lost in the middle") → format context có nhãn
nguồn → gọi OpenAI gpt-4o-mini → câu trả lời có citation.

Cấu hình & lý do:
    TOP_K=5      : đủ evidence, không quá dài gây lost-in-the-middle.
    TOP_P=0.9    : nucleus sampling đủ đa dạng nhưng không lan man.
    TEMPERATURE=0.3 : RAG cần factual, ít sáng tạo.

Chạy:
    python -m src.task10_generation
"""

import os

from dotenv import load_dotenv

load_dotenv()

from .task9_retrieval_pipeline import retrieve

# =============================================================================
# CONFIGURATION
# =============================================================================

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """Bạn trả lời câu hỏi một cách đầy đủ bằng tiếng Việt.
Với mỗi khẳng định hoặc dữ kiện, chèn ngay một citation trong ngoặc vuông trỏ
tới nguồn cụ thể (ví dụ: [Luật Phòng, chống ma túy 2021, Điều 28] hoặc
[VnExpress, 2024]).

Nếu thông tin KHÔNG có trong context được cung cấp, hãy nói
'Tôi không thể xác minh thông tin này từ nguồn hiện có' thay vì đoán.

Quy tắc:
- Chỉ dùng thông tin trong context được cung cấp.
- Mọi dữ kiện PHẢI có citation.
- Nếu context không đủ, nói rõ.
- Trình bày câu trả lời thành các đoạn rõ ràng."""


# =============================================================================
# DOCUMENT REORDERING (chống lost in the middle)
# =============================================================================

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp lại để chunk quan trọng nằm ở ĐẦU và CUỐI, kém quan trọng vào GIỮA.
    Input (theo score giảm dần): [1, 2, 3, 4, 5]
    Output:                      [1, 3, 5, 4, 2]
    """
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[0::2]         # vị trí chẵn (0,2,4...) → quan trọng nhất ở đầu
    back = chunks[1::2][::-1]    # vị trí lẻ (1,3...) đảo ngược → kém nhất vào giữa
    return front + back


# =============================================================================
# CONTEXT FORMATTING
# =============================================================================

def format_context(chunks: list[dict]) -> str:
    """Ghép chunks thành context, mỗi chunk có nhãn nguồn để LLM cite."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {}) or {}
        source = meta.get("source") or meta.get("title") or f"Nguồn {i}"
        doc_type = meta.get("type", "")
        parts.append(
            f"[Tài liệu {i} | Nguồn: {source}"
            f"{' | Loại: ' + doc_type if doc_type else ''}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


# =============================================================================
# GENERATION
# =============================================================================

def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    RAG end-to-end có citation.

    Returns:
        {'answer': str, 'sources': list[dict], 'retrieval_source': str}
    """
    chunks = retrieve(query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)

    user_message = f"Context:\n{context}\n\n---\n\nCâu hỏi: {query}"

    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )
    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("source", "hybrid") if chunks else "none",
    }


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma túy theo pháp luật Việt Nam?",
        "Những nghệ sĩ nào đã bị bắt vì liên quan tới ma túy?",
        "Quy trình cai nghiện ma túy bắt buộc theo Luật Phòng chống ma túy 2021?",
    ]
    for q in test_queries:
        print(f"\n{'=' * 70}\nQ: {q}\n{'=' * 70}")
        result = generate_with_citation(q)
        print(f"\n{result['answer']}")
        print(f"\n[Sources: {len(result['sources'])} chunks | via {result['retrieval_source']}]")
