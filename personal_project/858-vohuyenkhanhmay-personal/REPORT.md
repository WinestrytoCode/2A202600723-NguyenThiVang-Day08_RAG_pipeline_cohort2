# BÁO CÁO CÁ NHÂN — Day 8: RAG Pipeline (Pháp luật ma túy + Tin tức nghệ sĩ)

**Người thực hiện:** Vo Huyen Khanh May · **Kết quả:** `pytest tests/ -v` → **35 passed (10/10 task, 50/50 điểm)**

---

## 1. Tổng quan

Xây dựng pipeline RAG end-to-end trên chủ đề **pháp luật Việt Nam về ma túy** + **tin tức nghệ sĩ liên quan ma túy**: thu thập dữ liệu → chuẩn hoá markdown → chunk & index → tìm kiếm hybrid (semantic + lexical) → rerank → fallback vectorless → sinh câu trả lời có citation.

**Luồng pipeline:**
```
PDF luật + bài báo
   │ task1 (tải PDF) / task2 (crawl báo)
   ▼
data/landing/{legal,news}
   │ task3 (markitdown / crawl HTML)
   ▼
data/standardized/{legal,news}/*.md   (5 legal + 11 news)
   │ task4: chunk (800/120) → embed bge-m3 → Qdrant (1561 điểm)
   ▼
Query ──┬─ task5 semantic_search (Qdrant cosine) ─┐
        ├─ task6 lexical_search (BM25)            ─┤ task9: RRF merge → rerank (task7)
        │                                          │        └─ score<0.3 → fallback task8 PageIndex
        ▼                                          ▼
   task10: reorder (chống lost-in-the-middle) → gpt-4o-mini → trả lời + citation
```

## 2. Stack công nghệ & lý do chọn

| Thành phần | Lựa chọn | Lý do |
|---|---|---|
| Vector store | **Qdrant** (embedded `./qdrant_data`) | Không cần Docker, persist ra đĩa, API gọn. (README gợi ý Weaviate — tôi chọn Qdrant đơn giản hơn cho lab.) |
| Embedding | **BAAI/bge-m3** (1024-dim, COSINE) | Multilingual, mạnh cho tiếng Việt, chạy local miễn phí. |
| Lexical | **BM25** (`rank-bm25`) | Bắt khớp keyword/điều luật chính xác (vd "Điều 249"). |
| Reranking | **BAAI/bge-reranker-v2-m3** (local) | Cross-encoder, điểm 0..1, tốt tiếng Việt. (Ban đầu dùng Jina API nhưng **hết balance** → chuyển local.) |
| Vectorless fallback | **PageIndex** (`PageIndexClient`) | Tree-search reasoning trên cấu trúc văn bản, không cần vector. |
| Generation | **OpenAI gpt-4o-mini** | Trả lời factual, rẻ; temp 0.3 / top_p 0.9 cho RAG. |

**Hợp đồng dữ liệu (xuyên suốt):** mọi hàm search trả `list[dict]` gồm `{'content', 'score', 'metadata'}` sort theo score giảm dần; `metadata = {source, type, chunk_index}`; task9 thêm `source ∈ {hybrid, pageindex}`.

## 3. Chi tiết & giải thích từng task

**Task 1 — Thu thập văn bản pháp luật** ([task1](src/task1_collect_legal_docs.py)): tải tự động 5 PDF từ Cổng TTĐT Chính phủ (`datafiles.chinhphu.vn`), kiểm tra magic bytes `%PDF` + size. Gồm Luật 73/2021, BLHS 2015 (bản hợp nhất 2025), NĐ 105/2021, NĐ 57/2022, NĐ 90/2024.

**Task 2 — Crawl bài báo** ([task2](src/task2_crawl_news.py)): crawl 11 bài (VnExpress, Tuổi Trẻ, Thanh Niên, Dân Trí) bằng **Crawl4AI** (Playwright). Điểm mấu chốt: dùng **css_selector theo từng báo** (VnExpress `.fck_detail`, Tuổi Trẻ/Thanh Niên `.detail-content`, Dân Trí `.singular-content`) để chỉ lấy **thân bài**, loại nav/menu/footer → JSON sạch (2–14KB thay vì ~112KB nếu lấy cả trang).

**Task 3 — Convert markdown** ([task3](src/task3_convert_markdown.py)): `markitdown[pdf]` cho legal, JSON→markdown + header cho news. Converter **tự bỏ qua + xoá** file trích text rỗng để không tạo .md hỏng.

**Task 4 — Chunking & Indexing** ([task4](src/task4_chunking_indexing.py)): `RecursiveCharacterTextSplitter` với separator tiếng Việt, **chunk_size=800 / overlap=120 ký tự** (~200 token, gọn 1 khoản/điều, overlap ~15% giữ ngữ cảnh; văn bản luật là text thường "Điều N." nên không dùng MarkdownHeaderSplitter). Embed bge-m3 `normalize_embeddings=True` (khớp COSINE). Index **1561 chunk** (1466 legal + 95 news) vào Qdrant collection `DrugLawDocs`. Re-index sạch (xoá+tạo lại collection), upsert theo lô 256.

**Task 5 — Semantic Search** ([task5](src/task5_semantic_search.py)): embed query cùng bge-m3 → `query_points`. `score = p.score` (COSINE đã là similarity, **không** đảo dấu kiểu Weaviate). Tái dùng model + client của task4 (singleton). *Kiểm chứng:* "hình phạt tàng trữ" → top‑1 **Điều 249 BLHS** (0.769).

**Task 6 — Lexical Search (BM25)** ([task6](src/task6_lexical_search.py)): build BM25 trên **cùng tập chunk** với task4 (để task9 fusion khớp đơn vị). Tokenize: chuẩn hoá **Unicode NFC** + lowercase + tách theo `\w` (giữ chữ có dấu, bỏ dấu câu — tránh "túy," ≠ "túy" và "ma tuý" ≠ "ma túy"). *Kiểm chứng:* "Điều 249" → đúng Điều 249 (BM25 24.62).

**Task 7 — Reranking** ([task7](src/task7_reranking.py)): cross-encoder local `bge-reranker-v2-m3`, điểm logit → **sigmoid → 0..1**. Kèm `rerank_rrf` (RRF, dedup theo source+chunk_index) và `rerank_mmr` (MMR diversity). Có **graceful fallback** giữ thứ tự điểm sẵn có nếu model lỗi. *Kiểm chứng:* "hình phạt tàng trữ" → Điều 249 (#1, 0.731), doc nhiễu "Python" bị đẩy cuối.

**Task 8 — PageIndex Vectorless** ([task8](src/task8_pageindex_vectorless.py)): `PageIndexClient` thật — upload `luat-phong-chong-ma-tuy-2021.pdf` (31 trang, async OCR+tree), **cache `doc_id`** (`data/pageindex_doc.json`) để không upload lại tốn credit. `submit_query`→poll`get_retrieval`→map `retrieved_nodes`. PageIndex **không có score số** → tổng hợp score theo rank. *Kiểm chứng:* "cai nghiện tự nguyện" → đúng Điều 28/30/36.

**Task 9 — Retrieval Pipeline** ([task9](src/task9_retrieval_pipeline.py)): semantic + lexical → **RRF merge** (gắn `source="hybrid"`) → **rerank** (điểm 0..1) → nếu rỗng hoặc `best_score < 0.3` → **fallback PageIndex**. *Lưu ý quan trọng:* ngưỡng 0.3 áp lên **điểm rerank (0..1)**, không áp lên điểm RRF (~0.03) — nên ngưỡng chỉ kích hoạt khi reranking bật. `try/except` quanh rerank để model lỗi không làm sập pipeline. *Kiểm chứng:* 3 query đều ra `[hybrid]` đúng, điểm ~0.73.

**Task 10 — Generation có Citation** ([task10](src/task10_generation.py)): `retrieve` → **reorder chống "lost in the middle"**: `front=chunks[0::2]; back=chunks[1::2][::-1]` → `[1,2,3,4,5]→[1,3,5,4,2]` (quan trọng nhất ở đầu/cuối, kém nhất vào giữa). Format context có nhãn `[Tài liệu i | Nguồn: ...]` → gpt-4o-mini (temp **0.3** factual, top_p **0.9**) với system prompt buộc **citation cho mọi dữ kiện**, thiếu evidence thì "Tôi không thể xác minh...". *Kiểm chứng:* "hình phạt tàng trữ" → trích đúng **Điều 249 BLHS** kèm `[Tài liệu 1 | Nguồn: bo-luat-hinh-su-2015.md]`.

## 4. Vấn đề gặp & cách xử lý (điểm nhấn)

1. **Scaffold viết theo Weaviate** → thay toàn bộ bằng Qdrant (`query_points`, `p.score` cosine, không dùng `1-distance`).
2. **4/5 PDF luật là bản scan ký số** (markitdown trích 0 ký tự) → **crawl toàn văn HTML** từ thuvienphapluat.vn (selector `.cldivContentDocVn`) cho NĐ 105/57/90; riêng BLHS dùng bản hợp nhất 2025 có text. ([crawl_legal_html.py](src/crawl_legal_html.py))
3. **Bài báo dính boilerplate** (nav/menu ~70%) → css_selector theo từng báo → chỉ lấy thân bài.
4. **Stub PageIndex là API bịa** (`pi.upload/pi.query`) → đọc source SDK, dùng API thật `PageIndexClient` (key `id` không phải `node_id`, `relevant_contents` là list-lồng-list).
5. **Jina reranker hết balance** (`AUTHZ_INSUFFICIENT_BALANCE`) → chuyển sang cross-encoder **local** (miễn phí, điểm 0..1 nên ngưỡng fallback đúng).
6. **Windows code page**: phải `set PYTHONUTF8=1` khi chạy để output tiếng Việt không crash (cp1252). Crawl4AI cần `playwright install chromium` một lần.

## 5. Kết quả chấm điểm (`pytest tests/ -v` → 35 passed)

| Task | Nội dung | Điểm | Trạng thái |
|---|---|---|---|
| 1 | Thu thập ≥3 văn bản pháp luật | 3 | ✅ 5 PDF |
| 2 | Crawl ≥5 bài báo | 3 | ✅ 11 bài (sạch) |
| 3 | Convert markdown | 4 | ✅ 5 legal + 11 news |
| 4 | Chunking + Indexing | 7 | ✅ 1561 chunk @ Qdrant |
| 5 | Semantic search | 6 | ✅ |
| 6 | Lexical search (BM25) | 6 | ✅ |
| 7 | Reranking | 6 | ✅ local cross-encoder |
| 8 | PageIndex vectorless | 4 | ✅ |
| 9 | Retrieval pipeline + fallback | 7 | ✅ |
| 10 | Generation + citation | 4 | ✅ |
| **Tổng** | | **50** | **✅ 35/35 test** |

## 6. Đối chiếu yêu cầu nộp bài (README.md)

- [x] `data/landing/legal/` có ≥3 file PDF/DOCX (>1KB) — **5 PDF**.
- [x] `data/landing/news/` có ≥5 file JSON có field `url` (>500 bytes) — **11 JSON**.
- [x] `data/standardized/` có markdown cho cả `legal/` và `news/`.
- [x] Task 4: ghi rõ trong code chunking strategy, chunk_size/overlap, embedding model + dimension và **lý do** (docstring + comment).
- [x] Task 5/6: trả đúng format `{content, score, metadata}`, sort giảm dần.
- [x] Task 7: reranking hoạt động, output re-sorted có `score`.
- [x] Task 8: `pageindex_search` trả kết quả gắn `source="pageindex"`.
- [x] Task 9: pipeline + fallback logic (`source ∈ {hybrid, pageindex}`).
- [x] Task 10: top_k/top_p giải thích trong comment; output có citation `[Nguồn]`; thiếu evidence → "Tôi không thể xác minh...".
- [x] `pytest tests/ -v` PASS toàn bộ (50đ).
- [x] `requirements.txt` cập nhật (qdrant-client, pageindex>=0.2.8, bỏ weaviate); `.env.example` → `.env` đã điền key.

## 7. Cách chạy lại (reproduce)

```cmd
:: 0) môi trường (cmd, venv đã có sẵn)
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m playwright install chromium      :: cho Crawl4AI (1 lần)
set PYTHONUTF8=1                            :: bắt buộc cho tiếng Việt trên Windows

:: 1) dữ liệu
python -m src.task1_collect_legal_docs     :: tải PDF luật
python -m src.task2_crawl_news             :: crawl 11 bài báo (sạch)
python -m src.task3_convert_markdown       :: PDF/JSON -> markdown
python -m src.crawl_legal_html             :: HTML fallback cho 3 NĐ scan

:: 2) index (tải bge-m3 ~2.3GB lần đầu; embed ~14 phút CPU)
python -m src.task4_chunking_indexing

:: 3) chạy thử từng module
python -m src.task5_semantic_search
python -m src.task6_lexical_search
python -m src.task7_reranking              :: tải bge-reranker ~2.3GB lần đầu
python -m src.task8_pageindex_vectorless
python -m src.task9_retrieval_pipeline
python -m src.task10_generation

:: 4) chấm điểm
python -m pytest tests/ -v                 :: -> 35 passed
```

> **API key cần trong `.env`:** `OPENAI_API_KEY` (task10), `PAGEINDEX_API_KEY` (task8). `JINA_API_KEY` không còn cần (đã chuyển reranker local).
