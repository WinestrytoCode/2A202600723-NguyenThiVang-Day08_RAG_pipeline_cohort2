# 📊 DrugLaw Search — Evaluation Report

_Generated: 2026-06-08 07:51_

---

## 1. Config A/B Comparison

| Config | Tests | Failures | Fail% | P@3 | Recall@5 | MRR | NDCG@5 | AvgScore |
|--------|-------|----------|-------|-----|----------|-----|--------|----------|
| **hybrid_rerank** | 20 | 7 | 35% | 0.650 | 0.750 | 0.700 | 0.711 | 0.845 |
| **hybrid_no_rerank** | 20 | 20 | 100% | 0.467 | 0.750 | 0.558 | 0.616 | 0.049 |

> 🏆 **Best config by NDCG@5:** `hybrid_rerank`

---
## 2. Worst Performers

### 1. [legal_003] `Danh mục các chất ma tuý thuộc nhóm I theo quy định pháp luật Việt Nam gồm những`
- **Category:** phân loại ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.00, MRR=0.00, score=0.98
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [legal] `nghi-dinh-57-2022-nd-cp.md` score=0.981: **Điều 1. Danh mục các chất ma túy và tiền chất**
Ban hành kèm theo Nghị định này Phụ lục các danh m...
  - #2 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.399: a) Nghiên cứu các chất ma túy, tiền chất theo Danh mục chất ma túy và tiền chất do Chính phủ quy địn...
  - #3 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.161: a) Nghiên cứu, vận chuyển các chất ma túy quy định tại các Danh mục chất ma túy do Chính phủ quy địn...

### 2. [news_003] `Diễn viên Hữu Tín bị kết án bao nhiêu năm tù?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.43
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5 | Doc type mismatch: 3/3 top results are NOT 'news'

**Top 3 Results Returned:**
  - #1 [legal] `bo-luat-hinh-su-2015.md` score=0.431: ngoại của Việt Nam;

g) Dẫn đến biểu tình.

3.  Người  phạm  tội  còn  có  thể  bị  phạt  tiền  từ  ...
  - #2 [legal] `bo-luat-hinh-su-2015.md` score=0.074: Điều 108. Tội phản bội Tổ quốc

1. Công dân Việt Nam nào câu kết với nước ngoài nhằm gây nguy hại ...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.065: Điều này.

2.28 Không áp dụng quy định của Điều này đối với người bị kết án thuộc một

trong các tr...

### 3. [news_004] `Ca sĩ Châu Việt Cường bị kết án bao nhiêu năm?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.07
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.07 (< 0.3) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [legal] `bo-luat-hinh-su-2015.md` score=0.066: Điều 108. Tội phản bội Tổ quốc

1. Công dân Việt Nam nào câu kết với nước ngoài nhằm gây nguy hại ...
  - #2 [news] `article_11.md` score=0.001: Liên quan đến vụ án, Võ Thị Kim Tuyến, 38 tuổi, cùng 29 người khác bị cáo buộc tội *Mua bán, Tổ chức...
  - #3 [news] `article_12.md` score=0.001: # Người mẫu Andrea Aybar và ca sĩ Chi Dân bị bắt

**Source:** https://vnexpress.net/nguoi-mau-andrea...

### 4. [news_005] `Ca sĩ Chu Bin bị bắt vì tội gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.48
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [news] `article_12.md` score=0.480: Nguyễn Trung Hiếu (35 tuổi, tức ca sĩ Chi Dân) và Nguyễn Đỗ Trúc Phương (nhân vật có tầm ảnh hưởng t...
  - #2 [news] `article_14.md` score=0.020: Mở rộng điều tra các chân rết trong đường dây, Phòng Cảnh sát điều tra tội phạm về ma túy Công an TP...
  - #3 [news] `article_12.md` score=0.015: # Người mẫu Andrea Aybar và ca sĩ Chi Dân bị bắt

**Source:** https://vnexpress.net/nguoi-mau-andrea...

### 5. [news_007] `Nghệ sĩ nào dính dáng đến ma túy trong showbiz Việt Nam?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.00, MRR=0.00, score=0.96
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | No relevant result in top 5

**Top 3 Results Returned:**
  - #1 [news] `article_09.md` score=0.964: Mỗi lần một nghệ sĩ dính bê bối ma túy, công chúng lại đặt ra câu hỏi quen thuộc: "Tại sao họ có tất...
  - #2 [news] `article_11.md` score=0.961: # Anh em ca sĩ Chi Dân rủ nhiều người chơi ma túy như thế nào - Báo VnExpress

**Source:** https://v...
  - #3 [news] `article_14.md` score=0.945: Ngày 21/3/2023, Quang tiếp tục gửi nhiều kiện hàng về Việt Nam. Một kiện ghi người gửi "Chị Hà", ngư...

### 6. [mixed_002] `Cảnh sát Nha Trang đang làm gì để phòng chống ma túy?`
- **Category:** phòng chống ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.33, MRR=1.00, score=1.00
- **Failure reasons:** Low Precision@3=0.33 (< 0.4) | Doc type mismatch: 2/3 top results are NOT 'news'

**Top 3 Results Returned:**
  - #1 [news] `article_16.md` score=0.998: Ngày 7-6, trao đổi với *Tuổi Trẻ Online,* thượng tá Đào Xuân Trường - Trưởng Công an phường [Nha Tra...
  - #2 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.068: 1. Chỉ đạo cơ quan chuyên trách phòng, chống tội phạm về ma túy thuộc Bộ đội Biên phòng chủ trì thực...
  - #3 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.047: Các cơ quan chuyên trách phòng, chống tội phạm về ma túy thuộc lực lượng Công an nhân dân, Bộ đội Bi...

### 7. [edge_001] `Ma túy đá là gì và hình phạt cho tội sản xuất ma túy đá?`
- **Category:** phân loại ma túy | **Difficulty:** hard
- **Metrics:** P@3=0.67, MRR=0.50, score=0.01
- **Failure reasons:** Low rerank score=0.01 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.015: 8. Tệ nạn ma túy là việc sử dụng trái phép chất ma túy, nghiện ma túy và các
hành  vi  vi  phạm  phá...
  - #2 [legal] `bo-luat-hinh-su-2015.md` score=0.007: gia đình họ, thì bị phạt cải tạo không giam  giữ đến 03 năm hoặc phạt tù từ 06
tháng đến 03 năm:...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.007: không giam giữ đến 03 năm hoặc phạt tù từ 01 năm đến 05 năm:...

### 8. [legal_001] `Hình phạt cho tội tàng trữ trái phép chất ma tuý theo Điều 249 Bộ luật Hình sự?`
- **Category:** hình phạt pháp luật | **Difficulty:** easy
- **Metrics:** P@3=1.00, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `bo-luat-hinh-su-2015.md` score=0.032: 6. Người phạm tội còn có thể bị phạt tiền từ 5.000.000 đồng đến 500.000.000
đồng, cấm đảm nhiệm chứ...
  - #2 [legal] `bo-luat-hinh-su-2015.md` score=0.031: 2. Tái phạm về tội này thì bị phạt tù từ 03 năm đến 05 năm.

242 Điều này được bổ sung theo quy định...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.016: 2. Hình phạt tử hình đã tuyên trước ngày 01 tháng 7 năm 2025 đối với người phạm tội về
các tội quy đ...

### 9. [legal_002] `Luật Phòng chống ma tuý 2021 quy định những hình thức cai nghiện nào?`
- **Category:** cai nghiện | **Difficulty:** easy
- **Metrics:** P@3=1.00, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.031: 1. Kể từ ngày Luật này có hiệu lực thi hành:

a) Người đang thực hiện cai nghiện ma túy tự nguyện tạ...
  - #2 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.030: 2. Trong thời hạn 02 năm kể từ ngày Luật này có hiệu lực thi hành, cơ sở
cai nghiện ma túy bắt buộc ...
  - #3 [legal] `nghi-dinh-57-2022-nd-cp.md` score=0.016: **_Ghi chú:_** Bộ Nông nghiệp và Phát triển nông thôn có trách nhiệm quản lý các tiền chất dùng làm ...

### 10. [legal_004] `Tội mua bán trái phép chất ma tuý bị phạt tù bao nhiêu năm?`
- **Category:** hình phạt pháp luật | **Difficulty:** medium
- **Metrics:** P@3=0.67, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `bo-luat-hinh-su-2015.md` score=0.031: bán trái phép hoặc chiếm đoạt chất phóng xạ, vật liệu hạt nhân300

1. Người nào sản xuất, tàng trữ,...
  - #2 [legal] `bo-luat-hinh-su-2015.md` score=0.031: 5. Người phạm tội còn có thể bị phạt tiền từ 5.000.000 đồng đến 500.000.000
đồng, cấm đảm nhiệm chứ...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.016: 3. Trong trường hợp một người phải chấp hành nhiều bản án đã có hiệu lực
pháp luật mà các hình phạt...

### 11. [legal_005] `Điều kiện để được áp dụng biện pháp cai nghiện bắt buộc theo pháp luật Việt Nam?`
- **Category:** cai nghiện | **Difficulty:** hard
- **Metrics:** P@3=0.00, MRR=0.25, score=0.02
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.02 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `bo-luat-hinh-su-2015.md` score=0.016: năm đến 05 năm.

Điều 232. Tội vi phạm quy định về khai thác, bảo vệ rừng và lâm sản193
1.194 Người ...
  - #2 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.016: Điều 28. Các biện pháp cai nghiện ma túy

1. Biện pháp cai nghiện ma túy bao gồm:

a) Cai nghiện ma ...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.016: 191

100.000.000 đồng, phạt quản chế, cấm cư trú từ 01 năm đến 05 năm hoặc tịch thu
một phần hoặc t...

### 12. [legal_006] `Nghị định 116/2021/NĐ-CP quy định về vấn đề gì liên quan đến ma túy?`
- **Category:** nghị định | **Difficulty:** medium
- **Metrics:** P@3=0.33, MRR=1.00, score=0.02
- **Failure reasons:** Low Precision@3=0.33 (< 0.4) | Low rerank score=0.02 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.016: |  **CHÍNH PHỦ  
-------**  |  **CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM  
Độc lập - Tự do - Hạnh phúc  
...
  - #2 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.016: luật Hải quan; thực hiện quy định về phối hợp kiểm soát các hoạt động hợp pháp liên quan đến ma túy ...
  - #3 [legal] `nghi-dinh-57-2022-nd-cp.md` score=0.016: . Nghị định số [73/2018/NĐ-CP](https://thuvienphapluat.vn/van-ban/van-hoa-xa-hoi/nghi-dinh-73-2018-n...

### 13. [legal_007] `Người sử dụng trái phép chất ma tuý nhưng chưa đến mức bị truy cứu hình sự bị xử`
- **Category:** hình phạt pháp luật | **Difficulty:** medium
- **Metrics:** P@3=0.00, MRR=0.25, score=0.03
- **Failure reasons:** Low Precision@3=0.00 (< 0.4) | Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.032: e) Người có mặt tại các địa điểm có hành vi tổ chức, chứa chấp hoặc sử dụng trái phép chất ma túy nh...
  - #2 [legal] `luat-phong-chong-ma-tuy-2021.md` score=0.032: 8. Tệ nạn ma túy là việc sử dụng trái phép chất ma túy, nghiện ma túy và các
hành  vi  vi  phạm  phá...
  - #3 [legal] `nghi-dinh-105-2021-nd-cp.md` score=0.028: **Chương IV**
**QUẢN LÝ NGƯỜI SỬ DỤNG TRÁI PHÉP CHẤT MA TÚY**
**Điều 37. Đối tượng bị quản lý**
Đối ...

### 14. [news_001] `Ca sĩ Chi Dân bị bắt vì lý do gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=1.00, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_12.md` score=0.032: # Người mẫu Andrea Aybar và ca sĩ Chi Dân bị bắt

**Source:** https://vnexpress.net/nguoi-mau-andrea...
  - #2 [news] `article_12.md` score=0.031: Nguyễn Trung Hiếu (35 tuổi, tức ca sĩ Chi Dân) và Nguyễn Đỗ Trúc Phương (nhân vật có tầm ảnh hưởng t...
  - #3 [news] `article_13.md` score=0.028: ![Ca sĩ Chi Dân khi bị bắt. Ảnh: Công an cung cấp](data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAE...

### 15. [news_002] `Người mẫu An Tây bị truy tố những tội gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** easy
- **Metrics:** P@3=0.67, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_12.md` score=0.031: Theo nguồn tin, trước đó, chiều 9/11, cảnh sát kiểm tra căn hộ chung cư tại phường Thạnh Mỹ Lợi (TP ...
  - #2 [legal] `bo-luat-hinh-su-2015.md` score=0.016: Nếu người bị kết án đã bị tạm giữ, tạm giam thì thời gian tạm giữ, tạm giam
được trừ vào thời gian c...
  - #3 [news] `article_13.md` score=0.016: Trong vụ án còn có Nguyễn Trung Hiếu (ca sĩ Chi Dân) cùng anh trai Nguyễn Trung Tín, 44 tuổi; Nguyễn...

### 16. [news_006] `Vụ án 4 tiếp viên hàng không liên quan đến ma tuý như thế nào?`
- **Category:** vụ án lớn | **Difficulty:** medium
- **Metrics:** P@3=1.00, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_14.md` score=0.032: # Trùm ma túy đứng sau đường dây liên quan 4 tiếp viên hàng không - Báo VnExpress

**Source:** https...
  - #2 [news] `article_14.md` score=0.032: ![Những tuýp kem đánh răng chứa ma túy được các tiếp viên hàng không xách về Việt Nam. Ảnh: Hải quan...
  - #3 [news] `article_13.md` score=0.031: Kết quả điều tra xác định, 4 tiếp viên hàng không không quen biết, không phát sinh liên lạc và giao ...

### 17. [news_008] `Tại sao nhiều nghệ sĩ lại sa ngã vào ma tuý?`
- **Category:** phân tích xã hội | **Difficulty:** medium
- **Metrics:** P@3=0.33, MRR=0.33, score=0.12
- **Failure reasons:** Low Precision@3=0.33 (< 0.4) | Low rerank score=0.12 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_04.md` score=0.119: [Đặt báo](https://order.tuoitre.vn/formOrder.aspx "Đặt báo")
[Đăng ký Tuổi Trẻ Sao](https://mediahub...
  - #2 [news] `article_06.md` score=0.119: [Thể thao](/the-thao.htm "Thể thao")

### [Tuyển Thụy Sĩ phát hoảng vì nơi tập luyện có rất nhiều rắ...
  - #3 [news] `article_09.md` score=0.033: Mỗi lần một nghệ sĩ dính bê bối ma túy, công chúng lại đặt ra câu hỏi quen thuộc: "Tại sao họ có tất...

### 18. [news_009] `Long Nhật là ai và tại sao bị bắt?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.33, MRR=0.33, score=0.12
- **Failure reasons:** Low Precision@3=0.33 (< 0.4) | Low rerank score=0.12 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_03.md` score=0.122: 06-06
[Vĩnh Long thi tuyển công chức 683 người hoạt động không chuyên trách](/vinh-long-thi-tuyen-co...
  - #2 [news] `article_01.md` score=0.041: [Đừng để đồng bằng 'ăn' chính mình](/dung-de-dong-bang-an-chinh-minh-20260605231650688.htm "Đừng để ...
  - #3 [news] `article_11.md` score=0.016: Cơ quan điều tra xác định, Chi Dân cùng anh trai đã có hành vi rủ rê, cung cấp ma túy nên phải chịu ...

### 19. [news_010] `Cô tiên từ thiện Trúc Phương bị bắt vì tội gì?`
- **Category:** nghệ sĩ và ma túy | **Difficulty:** medium
- **Metrics:** P@3=0.33, MRR=0.50, score=0.08
- **Failure reasons:** Low Precision@3=0.33 (< 0.4) | Low rerank score=0.08 (< 0.3)

**Top 3 Results Returned:**
  - #1 [news] `article_08.md` score=0.084: ### [ChatGPT sẽ được 'đập đi xây lại' trong vài tuần tới](/chatgpt-se-duoc-dap-di-xay-lai-trong-vai-...
  - #2 [news] `article_11.md` score=0.030: Cùng thời điểm Chi Dân bị phát hiện phạm tội, Công an TP HCM cũng bắt người mẫu, diễn viên Andrea Ay...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.016: đồng trở lên;

d) Có tổ chức nơi cầm cố tài sản cho người tham gia đánh bạc; có lắp đặt
trang thiết ...

### 20. [mixed_001] `Hành vi tổ chức sử dụng ma tuý bị phạt tù bao nhiêu năm và có những nghệ sĩ nào `
- **Category:** kết hợp pháp luật và tin tức | **Difficulty:** hard
- **Metrics:** P@3=1.00, MRR=1.00, score=0.03
- **Failure reasons:** Low rerank score=0.03 (< 0.3)

**Top 3 Results Returned:**
  - #1 [legal] `bo-luat-hinh-su-2015.md` score=0.028: 1. Người nào chiếm dụng chỗ ở, xây dựng nhà trái phép, đã bị xử phạt vi
phạm hành chính về hành vi n...
  - #2 [legal] `bo-luat-hinh-su-2015.md` score=0.016: Điều 300. Tội tài trợ khủng bố

1. Người nào huy động, hỗ trợ tiền, tài sản dưới bất kỳ hình thức ...
  - #3 [legal] `bo-luat-hinh-su-2015.md` score=0.016: quan, tổ chức

1. Người nào sửa chữa, làm sai lệch nội dung hộ chiếu, thị thực, hộ khẩu, hộ
tịch, cá...

---
## 3. Improvement Recommendations

- ⚠️ **Doc-type mismatch** (2x): Xem xét thêm bộ lọc `doc_type` trên frontend hoặc thêm metadata vào query để hướng retrieval về đúng loại tài liệu.
- ⚠️ **Low rerank score** (15x): Cân nhắc thu thập thêm dữ liệu cho các chủ đề còn thiếu hoặc cải thiện chất lượng chunks.
- ⚠️ **Low precision** (12x): Thử tăng `CHUNK_OVERLAP` trong task4 hoặc sử dụng SemanticChunker thay RecursiveCharacter.

---
## 4. Query Log Summary

| Metric | Value |
|--------|-------|
| Total logged queries | 275 |
| Eval failures | 160 |
| Live user failures | 72 |
| Log file | `/home/winie/2A202600723-NguyenThiVang-Day08_RAG_pipeline_cohort2/group_project/evaluation/logs/query_failures.jsonl` |