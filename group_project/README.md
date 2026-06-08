# ⚖️ DrugLaw Search & RAG Chatbot

Hệ thống Tìm kiếm Lai (Hybrid Search) kết hợp Hỏi đáp (RAG Chatbot) về **Pháp luật phòng chống ma túy** và **Tin tức xã hội liên quan**.

---

## 🗺️ Kiến Trúc Hệ Thống

Dưới đây là sơ đồ luồng hoạt động chi tiết từ yêu cầu của User đến kết quả tìm kiếm và câu trả lời RAG:

```mermaid
graph TD
    %% Styling
    classDef client fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px,color:#0277bd;
    classDef server fill:#efebe9,stroke:#8d6e63,stroke-width:2px,color:#4e342e;
    classDef db fill:#e8f5e9,stroke:#4caf50,stroke-width:2px,color:#1b5e20;
    classDef model fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#4a148c;
    classDef pipe fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#e65100;
    
    subgraph UI ["Giao diện Người dùng (Frontend)"]
        User(["User Client"]) -->|1. Nhập câu hỏi| WebUI["Vanilla JS Web App (app.js)"]
        WebUI -->|Hiển thị kết quả & Chat| User
    end

    subgraph Backend ["FastAPI API Server (main.py)"]
        WebUI -->|2. HTTP POST /api/search| API["FastAPI Controller"]
        API -->|6. Ghi nhật ký truy vấn| QueryLogger["Query Failure Logger"]
        QueryLogger -->|7. Lưu trữ logs| JSONL[("query_failures.jsonl")]
        
        subgraph Pipeline ["Pipeline Truy vấn Lai (task9_retrieval_pipeline.py)"]
            API -->|3. Route truy vấn| Retrieve["retrieve() Orchestrator"]
            
            %% Dense Search
            Retrieve -->|Truy vấn Ngữ nghĩa| Dense["Semantic Search (task5)"]
            Dense -->|Tính vector truy vấn| DenseEmbed["MiniLM Embedding Model"]
            Dense -->|Tìm kiếm Khoảng cách| ChromaDB[("ChromaDB Vector Store")]
            
            %% Sparse Search
            Retrieve -->|Truy vấn Từ khóa| Sparse["Lexical Search (task6)"]
            Sparse -->|Điểm số BM25| BM25["BM25Okapi Index"]
            
            %% Fusion
            Dense -->|Top-2K Dense| Fusion["RRF Fusion (Reciprocal Rank Fusion)"]
            Sparse -->|Top-2K Sparse| Fusion
            
            %% Rerank
            Fusion -->|Hợp nhất ứng viên| Rerank["Reranker (task7)"]
            Rerank -->|Sigmoid Normalization| CEModel["mMARCO Cross-Encoder Model"]
            
            %% Fallback
            Rerank -->|Top Results| FallbackCheck{"Top Score < 0.3?"}
            FallbackCheck -->|Đúng (Fallback)| PageIndex["PageIndex Vectorless Search (task8)"]
            FallbackCheck -->|Sai (Đủ tốt)| FinalDocs["Final Retrieved Context Chunks"]
            PageIndex -->|Kết quả cấu trúc| FinalDocs
        end
        
        subgraph Generation ["RAG Generation (task10_generation.py)"]
            API -->|4. Tạo câu trả lời| Gen["generate_with_citation()"]
            FinalDocs -->|Truyền ngữ cảnh| Gen
            Gen -->|Tránh trôi thông tin giữa| Reorder["Document Reordering [1, 3, 5, 4, 2]"]
            Reorder -->|Chèn Prompt và Context| LLM["litellm (gpt-4o-mini)"]
            LLM -->|5. Trả lời kèm Trích dẫn| API
        end
    end
    
    class WebUI client;
    class API,QueryLogger server;
    class ChromaDB,BM25,JSONL db;
    class DenseEmbed,CEModel,LLM model;
    class Retrieve,Dense,Sparse,Fusion,Rerank,PageIndex,Gen,Reorder pipe;
```

---

## 🛠️ Chi Tiết Triển Khai Các Thành Phần

### 1. Thu thập & Chuẩn hóa dữ liệu (Task 1 - 3)
*   **Văn bản Pháp luật:** Thu thập các tài liệu PDF/DOCX chính thống (Bộ luật Hình sự, Luật Phòng chống ma túy 2021, Nghị định 116/2021/NĐ-CP).
*   **Tin tức Báo chí:** Sử dụng thư viện `Crawl4AI` thu thập tự động các bài báo chính quy về showbiz và các sự việc liên quan đến chất cấm.
*   **Chuẩn hóa:** Toàn bộ tài liệu raw được chuyển đổi đồng bộ sang định dạng Markdown thông qua thư viện `MarkItDown` của Microsoft để giữ cấu trúc bảng biểu và tiêu đề tốt nhất.

### 2. Chunking & Indexing (Task 4)
*   **Phương pháp:** Sử dụng `RecursiveCharacterTextSplitter` với kích thước `CHUNK_SIZE = 500` ký tự và `CHUNK_OVERLAP = 50`.
*   **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) gọn nhẹ, phù hợp cho việc chạy local thời gian thực.
*   **Vector Database:** `ChromaDB` (Persistent Client) lưu trữ vector cục bộ.

### 3. Tìm Kiếm Lai & Reranking (Task 5 - 7)
*   **Lexical Search:** Sử dụng thuật toán `BM25Okapi` phân tách từ khóa tiếng Việt.
*   **Semantic Search:** Truy vấn khoảng cách Cosine trên cơ sở dữ liệu vector ChromaDB.
*   **Reciprocal Rank Fusion (RRF):** Kết hợp kết quả từ hai bộ tìm kiếm với hằng số phạt vị trí hạng $k=60$.
*   **Cross-Encoder Reranker:** Sử dụng mô hình đa ngôn ngữ chuyên dụng cho tiếng Việt `unicamp-dl/mminiLM-L6-v2-mmarco-v2`. Điểm logit đầu ra được chuẩn hóa qua hàm **Sigmoid** để ánh xạ điểm liên quan về đoạn $[0.0, 1.0]$.
*   **Model Caching:** Tối ưu hóa tải mô hình toàn cục giúp giảm độ trễ phản hồi từ ~3.5 giây xuống **< 0.1 giây** mỗi truy vấn.

### 4. Cơ chế Fallback sang PageIndex (Task 8 - 9)
*   Nếu điểm số của kết quả tìm kiếm lai sau Rerank nhỏ hơn `score_threshold = 0.3` (tức hệ thống không tìm thấy tài liệu phù hợp trong DB cục bộ), hệ thống tự động fallback sang dịch vụ **PageIndex Vectorless RAG** để khai thác cấu trúc thông tin nâng cao và trả về kết quả có độ bao phủ cao hơn.

### 5. Sinh Câu Trả Lời có Citation (Task 10)
*   **Document Reordering:** Sắp xếp lại thứ tự các chunk trước khi đưa vào LLM theo mô hình: đưa chunk quan trọng nhất lên đầu và cuối ngữ cảnh, các chunk ít quan trọng ở giữa (mô hình `[1, 3, 5, 4, 2]`) nhằm tránh hiện tượng **"Lost in the Middle"**.
*   **Prompt trích dẫn:** Ép buộc LLM chỉ trả lời dựa vào context được cung cấp và đính kèm nhãn trích dẫn dạng `[Tên nguồn, Năm]` hoặc `[Điều luật]`.
*   **Nhận biết giới hạn:** LLM trả về *"Tôi không thể xác minh thông tin này từ nguồn hiện có"* nếu thông tin cung cấp bị thiếu hụt.

---

## 📊 Đánh Giá & Benchmark A/B

Hệ thống được đánh giá tự động dựa trên **Golden Dataset gồm 20 câu hỏi** đa dạng mức độ khó và loại tài liệu.

### 1. Bảng Điểm So Sánh A/B

| Config | Tổng số Tests | Số truy vấn thất bại | Tỉ lệ lỗi | Precision@3 | Recall@5 | MRR | NDCG@5 | Điểm TB (Score) |
|--------|:-------------:|:--------------------:|:---------:|:-----------:|:--------:|:---:|:------:|:---------------:|
| **hybrid_rerank** | 20 | 12 | 60% | **0.433** | **0.550** | **0.470** | **0.484** | **0.608** |
| **hybrid_no_rerank** | 20 | 20 | 100% | 0.300 | 0.500 | 0.317 | 0.387 | 0.102 |

> 🏆 **Cấu hình tối ưu nhất:** `hybrid_rerank` mang lại hiệu quả vượt trội ở tất cả các chỉ số chất lượng tìm kiếm (NDCG@5 tăng 25%, MRR tăng 48% so với không rerank).

---

### 2. Phân Tích Worst Performers (Các Trường Hợp Lỗi Điển Hình)

Từ bảng logs chi tiết tại [results.md](file:///home/winie/2A202600723-NguyenThiVang-Day08_RAG_pipeline_cohort2/group_project/evaluation/results.md):
1.  **Lỗi Nhầm Lẫn Loại Tài Liệu (Doc-type Mismatch):**
    *   *Truy vấn:* `"Hình phạt cho tội tàng trữ trái phép chất ma tuý theo Điều 249 Bộ luật Hình sự?"` (Loại mong đợi: `legal`).
    *   *Vấn đề:* Hệ thống trả về 3 kết quả hàng đầu là tin tức báo chí (`[news]`) nói về nghệ sĩ Chi Dân bị bắt do tàng trữ ma túy.
    *   *Nguyên nhân:* Từ khóa `"tàng trữ ma túy"` và `"hình phạt"` xuất hiện dày đặc trong cả văn bản luật và tin báo chí. Tuy nhiên, mật độ từ khóa ở các bài báo thường cao hơn và văn phong tự nhiên hơn nên mô hình ngữ nghĩa MiniLM và BM25 ưu tiên các bài báo giải trí trước.
2.  **Điểm Số Rerank Thấp (Low Rerank Score):**
    *   *Truy vấn:* `"Điều kiện để được áp dụng biện pháp cai nghiện bắt buộc theo pháp luật Việt Nam?"`
    *   *Vấn đề:* Không tìm thấy kết quả phù hợp nào trong top 5 hoặc điểm số rerank về $0.0$.
    *   *Nguyên nhân:* Chunking tĩnh vô tình chia cắt các điều luật liên quan của Nghị định 116 làm mất liên kết ngữ cảnh khiến mô hình Cross-Encoder không khớp được với truy vấn dài mang tính học thuật cao.

---

### 3. Đề Xuất Cải Tiến Để Tăng Độ Chính Xác (Accuracy Improvement)

1.  **Phân loại Intent (Intent Classification) & Metadata Filtering:**
    *   *Giải pháp:* Dùng một bộ phân loại truy vấn đơn giản (bằng regex hoặc LLM nhỏ) để nhận diện người dùng đang hỏi về điều luật (`legal`) hay tin tức showbiz (`news`).
    *   *Hành động:* Áp dụng metadata filter `doc_type` trực tiếp khi query ChromaDB. Điều này sẽ giải quyết triệt để 100% các lỗi Doc-type mismatch.
2.  **Chuyển sang Chunking Theo Phân Cấp (Hierarchical / Markdown Chunker):**
    *   *Hành động:* Thay vì chia đoạn theo độ dài ký tự tĩnh (500), chia chunk dựa trên tiêu đề `## Điều...` của văn bản pháp luật giúp giữ nguyên vẹn nội dung của từng điều khoản quy định.
3.  **Tăng Kích Thước Overlap (Chunk Overlap):**
    *   *Hành động:* Tăng `CHUNK_OVERLAP` từ `50` lên `100 - 150` để các chunk kế cận không bị mất thông tin chuyển tiếp.

---

## 👥 Phân Công Công Việc Nhóm

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|---|---|---|---|
| **Nguyễn Thị Vàng** | *Leader* | Thiết kế hệ thống, Crawl tin tức (Task 2), Chuẩn hóa dữ liệu (Task 1, 3). | ✅ Hoàn thành |
| **Thành viên 2** | *Search Dev* | Xây dựng index dữ liệu ChromaDB, tối ưu hoá bộ mã hóa dense/sparse (Task 4-6). | ✅ Hoàn thành |
| **Thành viên 3** | *Rerank Dev* | Tích hợp Cross-Encoder Reranker đa ngôn ngữ tiếng Việt & PageIndex Fallback (Task 7-9). | ✅ Hoàn thành |
| **Thành viên 4** | *RAG & QA* | Viết cơ chế Generation, thiết lập pipeline đánh giá A/B & query failure logger. | ✅ Hoàn thành |

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Chuẩn Bị Môi Trường
Cài đặt toàn bộ các thư viện liên quan:
```bash
pip install -r requirements.txt
```

Cấu hình các API Key cần thiết trong file `.env` tại thư mục gốc:
```env
OPENAI_API_KEY=your_openai_key
PAGEINDEX_API_KEY=your_pageindex_key
```

### 2. Thu Thập Dữ Liệu & Indexing
Chạy các scripts thu thập dữ liệu và lưu trữ vào Vector Store:
```bash
# 1. Tải văn bản pháp luật và tin tức báo chí
python3 src/task1_collect_legal_docs.py
python3 src/task2_crawl_news.py

# 2. Chuẩn hóa dữ liệu sang Markdown
python3 src/task3_convert_markdown.py

# 3. Phân đoạn và lập chỉ mục vào Vector Store
python3 src/task4_chunking_indexing.py
```

### 3. Khởi Chạy API Server Backend & UI Frontend
Chạy server backend FastAPI (đã được tối ưu hóa tải mô hình):
```bash
python3 group_project/run_server.py
```
*   **Trang chủ tìm kiếm (Frontend UI):** `http://localhost:8000/`
*   **Tài liệu Swagger API:** `http://localhost:8000/docs`

### 4. Khởi Chạy Giao Diện Chatbot RAG (Streamlit)
```bash
streamlit run group_project/search_app.py
```
*   Ứng dụng sẽ tự động mở tại địa chỉ `http://localhost:8501/`.

### 5. Chạy Báo Cáo Đánh Giá Chất Lượng (Evaluation)
Để kiểm tra độ chính xác và so sánh cấu hình A/B Reranking bất cứ lúc nào:
```bash
python3 group_project/evaluation/eval_pipeline.py
```
Báo cáo chi tiết sẽ được tự động xuất ra tại file `group_project/evaluation/results.md`.
