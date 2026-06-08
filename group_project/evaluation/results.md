# 📊 DrugLaw Search — Evaluation Report

_Generated: 2026-06-08 04:10_

---

## 1. Config A/B Comparison

| Config | Tests | Failures | Fail% | P@3 | Recall@5 | MRR | NDCG@5 | AvgScore |
|--------|-------|----------|-------|-----|----------|-----|--------|----------|
| **hybrid_rerank** | 20 | 12 | 60% | 0.433 | 0.550 | 0.470 | 0.484 | 0.608 |
| **hybrid_no_rerank** | 20 | 20 | 100% | 0.300 | 0.500 | 0.317 | 0.387 | 0.102 |

> 🏆 **Best config by NDCG@5:** `hybrid_rerank`

---
## 2. Worst Performers

### 1. [legal_001] `Hình phạt cho tội tàng trữ trái phép chất ma tuý theo Điều 249 Bộ luật Hình sự?`
- **Category:** hình phạt pháp luật | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.34
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'legal'

**Top 3 Results Returned:**
  - #1 [news] `article_11.md` score=0.340: Cơ quan điều tra xác định, Chi Dân cùng anh trai đã có hành vi rủ rê, cung cấp ma túy nên phải chịu ...
  - #2 [news] `article_12.md` score=0.136: Nguyễn Trung Hiếu (35 tuổi, tức ca sĩ Chi Dân) và Nguyễn Đỗ Trúc Phương (nhân vật có tầm ảnh hưởng t...
  - #3 [news] `article_11.md` score=0.130: Liên quan đến vụ án, Võ Thị Kim Tuyến, 38 tuổi, cùng 29 người khác bị cáo buộc tội *Mua bán, Tổ chức...

### 2. [legal_002] `Luật Phòng chống ma tuý 2021 quy định những hình thức cai nghiện nào?`
- **Category:** cai nghiện | **Difficulty:** easy
- **Metrics:** P@3=0.67, MRR=1.00, score=0.02
- **Failure reasons:** Low rerank score=0.02 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.019: chong ma tuy 2021

Dieu 1. Pham vi dieu chinh

Luat nay quy dinh ve phong, chong ma tuy, quan ly ngu...
  - #2 [news] `article_12.md` score=0.002: Chuyên án đã triệt phá tổng cộng gần 500 đường dây, băng nhóm tội phạm; khởi tố 1.132 bị can; xử phạ...
  - #3 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.001: Luat Phong, chong ma tuy 2021 (73/2021/QH15)

Luat Phong, chong ma tuy 2021

Dieu 1. Pham vi dieu ch...

### 3. [legal_003] `Danh mục các chất ma tuý thuộc nhóm I theo quy định pháp luật Việt Nam gồm những`
- **Category:** phân loại ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.00, MRR=0.00, score=0.00
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.00 (< 0.3) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'legal'

**Top 3 Results Returned:**
  - #1 [news] `article_11.md` score=0.002: Động thái này được đưa ra trong quá trình mở rộng, truy xét toàn bộ đường dây tội phạm vận chuyển tr...
  - #2 [news] `article_12.md` score=0.001: Động thái này của Công an TP HCM được đưa ra trong quá trình mở rộng, truy xét toàn bộ đường dây tội...
  - #3 [news] `article_16.md` score=0.000: Công an tỉnh Khánh Hòa cũng vừa phát đi cảnh báo về sự xuất hiện của nhiều loại ma túy mới được ngụy...

### 4. [legal_004] `Tội mua bán trái phép chất ma tuý bị phạt tù bao nhiêu năm?`
- **Category:** hình phạt pháp luật | **Difficulty:** medium
- **Metrics:** P@3=0.00, MRR=0.00, score=0.90
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'legal'

**Top 3 Results Returned:**
  - #1 [news] `article_11.md` score=0.898: Liên quan đến vụ án, Võ Thị Kim Tuyến, 38 tuổi, cùng 29 người khác bị cáo buộc tội *Mua bán, Tổ chức...
  - #2 [news] `article_12.md` score=0.893: Chuyên án đã triệt phá tổng cộng gần 500 đường dây, băng nhóm tội phạm; khởi tố 1.132 bị can; xử phạ...
  - #3 [news] `article_13.md` score=0.290: ---

Ngày 2/4, VKSND TP HCM đã hoàn tất cáo trạng truy tố Hoàng Sỹ Thắng cùng 226 người khác, chuyển...

### 5. [legal_005] `Điều kiện để được áp dụng biện pháp cai nghiện bắt buộc theo pháp luật Việt Nam?`
- **Category:** cai nghiện | **Difficulty:** hard
- **Metrics:** P@3=0.00, MRR=0.00, score=0.00
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.00 (< 0.3) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'legal'

**Top 3 Results Returned:**
  - #1 [news] `article_12.md` score=0.000: Theo Công an TP HCM, khi thực hiện đúng phương châm "không đánh khúc giữa, bắt cả đường dây, người c...
  - #2 [news] `article_14.md` score=0.000: **Kết quả giám định giọng nói xác định Nậm là người chỉ đạo đường dây**

Kết quả điều tra xác định, ...
  - #3 [news] `article_16.md` score=0.000: Điều này khiến việc nhận biết và phát hiện gặp nhiều khó khăn, tiềm ẩn nguy cơ ảnh hưởng nghiêm trọn...

### 6. [legal_006] `Nghị định 116/2021/NĐ-CP quy định về vấn đề gì liên quan đến ma túy?`
- **Category:** nghị định | **Difficulty:** medium
- **Metrics:** P@3=0.00, MRR=0.00, score=0.00
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.00 (< 0.3) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'legal'

**Top 3 Results Returned:**
  - #1 [news] `article_10.md` score=0.001: # Long Nhật được biết đến ra sao trước khi bị bắt liên quan ma túy

**Source:** https://vnexpress.ne...
  - #2 [news] `article_14.md` score=0.001: **Kết quả giám định giọng nói xác định Nậm là người chỉ đạo đường dây**

Kết quả điều tra xác định, ...
  - #3 [news] `article_11.md` score=0.001: Động thái này được đưa ra trong quá trình mở rộng, truy xét toàn bộ đường dây tội phạm vận chuyển tr...

### 7. [legal_007] `Người sử dụng trái phép chất ma tuý nhưng chưa đến mức bị truy cứu hình sự bị xử`
- **Category:** hình phạt pháp luật | **Difficulty:** medium
- **Metrics:** P@3=0.00, MRR=0.00, score=0.99
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'legal'

**Top 3 Results Returned:**
  - #1 [news] `article_12.md` score=0.991: Theo Công an TP HCM, khi thực hiện đúng phương châm "không đánh khúc giữa, bắt cả đường dây, người c...
  - #2 [news] `article_13.md` score=0.892: Trong vụ án còn có Nguyễn Trung Hiếu (ca sĩ Chi Dân) cùng anh trai Nguyễn Trung Tín, 44 tuổi; Nguyễn...
  - #3 [news] `article_11.md` score=0.832: Cơ quan điều tra xác định, Chi Dân cùng anh trai đã có hành vi rủ rê, cung cấp ma túy nên phải chịu ...

### 8. [news_003] `Diễn viên Hữu Tín bị kết án bao nhiêu năm tù?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.00
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.00 (< 0.3) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [news] `article_14.md` score=0.000: Nhà chức trách đã chứng minh số tiền giao dịch ma túy lên đến gần 29.000 tỷ đồng; chặt đứt gần 500 n...
  - #2 [news] `article_14.md` score=0.000: Chiều cùng ngày, Nậm gọi cho Thắng báo ma túy đã về đến Việt Nam, nhờ Thắng 2 lần chuyển tiền cho mộ...
  - #3 [news] `article_14.md` score=0.000: Ngày 21/3/2023, Quang tiếp tục gửi nhiều kiện hàng về Việt Nam. Một kiện ghi người gửi "Chị Hà", ngư...

### 9. [news_004] `Ca sĩ Châu Việt Cường bị kết án bao nhiêu năm?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.00
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.00 (< 0.3) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [news] `article_11.md` score=0.001: Liên quan đến vụ án, Võ Thị Kim Tuyến, 38 tuổi, cùng 29 người khác bị cáo buộc tội *Mua bán, Tổ chức...
  - #2 [news] `article_12.md` score=0.001: # Người mẫu Andrea Aybar và ca sĩ Chi Dân bị bắt

**Source:** https://vnexpress.net/nguoi-mau-andrea...
  - #3 [news] `article_13.md` score=0.000: ![Ca sĩ Chi Dân khi bị bắt. Ảnh: Công an cung cấp](data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAE...

### 10. [news_005] `Ca sĩ Chu Bin bị bắt vì tội gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.96
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [news] `article_11.md` score=0.964: Cơ quan điều tra xác định, Chi Dân cùng anh trai đã có hành vi rủ rê, cung cấp ma túy nên phải chịu ...
  - #2 [news] `article_12.md` score=0.480: Nguyễn Trung Hiếu (35 tuổi, tức ca sĩ Chi Dân) và Nguyễn Đỗ Trúc Phương (nhân vật có tầm ảnh hưởng t...
  - #3 [news] `article_11.md` score=0.101: Liên quan đến vụ án, Võ Thị Kim Tuyến, 38 tuổi, cùng 29 người khác bị cáo buộc tội *Mua bán, Tổ chức...

### 11. [news_007] `Nghệ sĩ nào dính dáng đến ma túy trong showbiz Việt Nam?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.20, score=0.96
- **Failure reasons:** Low Precision@3=0.00 (< 0.4)

**Top 3 Results Returned:**
  - #1 [news] `article_09.md` score=0.964: Mỗi lần một nghệ sĩ dính bê bối ma túy, công chúng lại đặt ra câu hỏi quen thuộc: "Tại sao họ có tất...
  - #2 [news] `article_11.md` score=0.961: # Anh em ca sĩ Chi Dân rủ nhiều người chơi ma túy như thế nào - Báo VnExpress

**Source:** https://v...
  - #3 [news] `article_14.md` score=0.945: Ngày 21/3/2023, Quang tiếp tục gửi nhiều kiện hàng về Việt Nam. Một kiện ghi người gửi "Chị Hà", ngư...

### 12. [edge_001] `Ma túy đá là gì và hình phạt cho tội sản xuất ma túy đá?`
- **Category:** phân loại ma túy | **Difficulty:** hard
- **Metrics:** P@3=0.00, MRR=0.20, score=0.03
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_11.md` score=0.025: Cơ quan điều tra xác định, Chi Dân cùng anh trai đã có hành vi rủ rê, cung cấp ma túy nên phải chịu ...
  - #2 [news] `article_14.md` score=0.001: Mở rộng điều tra các chân rết trong đường dây, Phòng Cảnh sát điều tra tội phạm về ma túy Công an TP...
  - #3 [news] `article_13.md` score=0.001: ---

Ngày 2/4, VKSND TP HCM đã hoàn tất cáo trạng truy tố Hoàng Sỹ Thắng cùng 226 người khác, chuyển...

### 13. [news_001] `Ca sĩ Chi Dân bị bắt vì lý do gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.67, MRR=0.50, score=0.10
- **Failure reasons:** Low rerank score=0.10 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_04.md` score=0.099: ### ['Cái bẫy' bất động sản của châu Á](/cai-bay-bat-dong-san-cua-chau-a-20260607141528489.htm "'Cái...
  - #2 [news] `article_12.md` score=0.032: # Người mẫu Andrea Aybar và ca sĩ Chi Dân bị bắt

**Source:** https://vnexpress.net/nguoi-mau-andrea...
  - #3 [news] `article_12.md` score=0.032: Nguyễn Trung Hiếu (35 tuổi, tức ca sĩ Chi Dân) và Nguyễn Đỗ Trúc Phương (nhân vật có tầm ảnh hưởng t...

### 14. [news_002] `Người mẫu An Tây bị truy tố những tội gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.67, MRR=0.50, score=0.07
- **Failure reasons:** Low rerank score=0.07 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_04.md` score=0.070: [Giải trí](/giai-tri.htm "Giải trí")

### [Mê vai tài phiệt của Heo Nam Jun, fan lại bất ngờ với gu ...
  - #2 [news] `article_12.md` score=0.031: Theo nguồn tin, trước đó, chiều 9/11, cảnh sát kiểm tra căn hộ chung cư tại phường Thạnh Mỹ Lợi (TP ...
  - #3 [news] `article_13.md` score=0.030: ---

Ngày 2/4, VKSND TP HCM đã hoàn tất cáo trạng truy tố Hoàng Sỹ Thắng cùng 226 người khác, chuyển...

### 15. [news_006] `Vụ án 4 tiếp viên hàng không liên quan đến ma tuý như thế nào?`
- **Category:** vụ án lớn | **Difficulty:** medium
- **Metrics:** P@3=1.00, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_14.md` score=0.032: # Trùm ma túy đứng sau đường dây liên quan 4 tiếp viên hàng không - Báo VnExpress

**Source:** https...
  - #2 [news] `article_14.md` score=0.032: ![Những tuýp kem đánh răng chứa ma túy được các tiếp viên hàng không xách về Việt Nam. Ảnh: Hải quan...
  - #3 [news] `article_13.md` score=0.032: Kết quả điều tra xác định, 4 tiếp viên hàng không không quen biết, không phát sinh liên lạc và giao ...

### 16. [news_008] `Tại sao nhiều nghệ sĩ lại sa ngã vào ma tuý?`
- **Category:** phân tích xã hội | **Difficulty:** medium
- **Metrics:** P@3=0.33, MRR=0.33, score=0.12
- **Failure reasons:** Low Precision@3=0.33 (< 0.4) | Low rerank score=0.12 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_04.md` score=0.119: [Đặt báo](https://order.tuoitre.vn/formOrder.aspx "Đặt báo")
[Đăng ký Tuổi Trẻ Sao](https://mediahub...
  - #2 [news] `article_07.md` score=0.119: [Thể thao](/the-thao.htm "Thể thao")

### [Tuyển Thụy Sĩ phát hoảng vì nơi tập luyện có rất nhiều rắ...
  - #3 [news] `article_09.md` score=0.033: Mỗi lần một nghệ sĩ dính bê bối ma túy, công chúng lại đặt ra câu hỏi quen thuộc: "Tại sao họ có tất...

### 17. [news_009] `Long Nhật là ai và tại sao bị bắt?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.67, MRR=0.50, score=0.12
- **Failure reasons:** Low rerank score=0.12 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_03.md` score=0.119: 06-06
[Vĩnh Long thi tuyển công chức 683 người hoạt động không chuyên trách](/vinh-long-thi-tuyen-co...
  - #2 [news] `article_04.md` score=0.115: [![Nhiều bảo tàng ở Đà Nẵng bắt đầu thu phí tham quan](https://cdn2.tuoitre.vn/zoom/260_163/47158475...
  - #3 [news] `article_12.md` score=0.032: # Người mẫu Andrea Aybar và ca sĩ Chi Dân bị bắt

**Source:** https://vnexpress.net/nguoi-mau-andrea...

### 18. [news_010] `Cô tiên từ thiện Trúc Phương bị bắt vì tội gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.67, MRR=0.50, score=0.06
- **Failure reasons:** Low rerank score=0.06 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_08.md` score=0.055: Từ ngày 1-1-2023, Tuổi Trẻ Online giới thiệu [**Tuổi Trẻ Sao**](https://mediahub.tuoitre.vn/tuoitres...
  - #2 [news] `article_11.md` score=0.032: Cùng thời điểm Chi Dân bị phát hiện phạm tội, Công an TP HCM cũng bắt người mẫu, diễn viên Andrea Ay...
  - #3 [news] `article_12.md` score=0.032: Nguyễn Trung Hiếu (35 tuổi, tức ca sĩ Chi Dân) và Nguyễn Đỗ Trúc Phương (nhân vật có tầm ảnh hưởng t...

### 19. [mixed_001] `Hành vi tổ chức sử dụng ma tuý bị phạt tù bao nhiêu năm và có những nghệ sĩ nào `
- **Category:** kết hợp pháp luật và tin tức | **Difficulty:** hard
- **Metrics:** P@3=0.67, MRR=0.50, score=0.04
- **Failure reasons:** Low rerank score=0.04 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `luat-an-ninh-quoc-gia-2004.md` score=0.041: khi cac to chuc toi pham su dung vu khi nong o khu vuc bien gioi.

Day la noi dung mo phong de dam b...
  - #2 [news] `article_11.md` score=0.032: Cùng thời điểm Chi Dân bị phát hiện phạm tội, Công an TP HCM cũng bắt người mẫu, diễn viên Andrea Ay...
  - #3 [news] `article_14.md` score=0.031: Hành vi của Nậm, Thắng cùng Bùi Văn Ánh (cháu rể) và 225 bị can thuộc Chuyên án VN10 được nêu trong ...

### 20. [mixed_002] `Cảnh sát Nha Trang đang làm gì để phòng chống ma túy?`
- **Category:** phòng chống ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.67, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_16.md` score=0.033: Bên cạnh đó, để công tác phòng chống ma túy được hiệu quả, Công an tỉnh Khánh Hòa đề nghị người dân ...
  - #2 [news] `article_16.md` score=0.032: Ngày 7-6, trao đổi với *Tuổi Trẻ Online,* thượng tá Đào Xuân Trường - Trưởng Công an phường [Nha Tra...
  - #3 [news] `article_15.md` score=0.031: Cảnh sát bắt nghi phạm khi vừa tiếp nhận lô hàng thuốc lắc được ngụy trang trong các gói thực phẩm c...

---
## 3. Improvement Recommendations

- ⚠️ **Doc-type mismatch** (6x): Xem xét thêm bộ lọc `doc_type` trên frontend hoặc thêm metadata vào query để hướng retrieval về đúng loại tài liệu.
- ⚠️ **Low rerank score** (15x): Cân nhắc thu thập thêm dữ liệu cho các chủ đề còn thiếu hoặc cải thiện chất lượng chunks.
- ⚠️ **Low precision** (12x): Thử tăng `CHUNK_OVERLAP` trong task4 hoặc sử dụng SemanticChunker thay RecursiveCharacter.

---
## 4. Query Log Summary

| Metric | Value |
|--------|-------|
| Total logged queries | 85 |
| Eval failures | 62 |
| Live user failures | 28 |
| Log file | `/home/winie/2A202600723-NguyenThiVang-Day08_RAG_pipeline_cohort2/group_project/evaluation/logs/query_failures.jsonl` |