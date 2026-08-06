# Project Journal

Ghi 5 phút cuối mỗi buổi làm việc. Không viết lại từ trí nhớ ở cuối tuần — ghi ngay lúc đó.

Format:
```markdown
## Week X — [ngày]
**Tried:** ...
**Result:** ...
**Reason:** ...
**Next:** ...
```

---

## Week 0 — [điền ngày]
**Tried:** Setup CI (pytest) cho repo trống, tạo PR đầu tiên qua Git flow
**Result:** CI fail 2 lần trước khi pass — lần 1 do pytest chưa được cài trong workflow, lần 2 do bash `-e` khiến script dừng trước khi kịp kiểm tra exit code của pytest
**Reason:** GitHub Actions chạy mỗi bước `run: |` bằng bash với cờ `-e` mặc định (dừng ngay khi có lệnh trả về mã khác 0) — `pytest; code=$?` không kịp chạy tới phần gán biến trước khi step bị dừng; phải dùng `set +e` trước khi chạy pytest rồi `set -e` lại sau khi đã lấy được exit code
**Next:** Bắt đầu học nội dung Week 0 — Embedding, Semantic Search, Dense/Sparse/Hybrid Retrieval, RAG, Chunking, LoRA/QLoRA cơ bản, các metric đánh giá

## Week 1 (Session 1) — 2026-07-28
**Tried:** Thu thập 16 tài liệu (15 hợp đồng từ 5 công ty + Luật Kinh doanh Bảo hiểm 2022), phân tích tay cấu trúc phân cấp, viết Data Profiling Report đầy đủ ([dataset.md](file:///d:/HocTap/Project_NLP_RAG/clausewise-ai/docs/dataset.md)).
**Result:** Phát hiện sự không đồng nhất cấu trúc nghiêm trọng (AIA 3 file 3 cấu trúc), 2 file Manulife dạng 2 cột, và 1 file Manulife image-only (0 ký tự trích xuất).
**Reason:** Không thể dùng hardcoded regex cho từng công ty vì cấu trúc gắn liền với tài liệu chứ không phải công ty. Cần thiết kế Document Structure Profiler tự thích ứng (ADR-002).
**Next:** Thiết kế chi tiết Ingestion Pipeline 2 lớp và nghiên cứu giải pháp trích xuất layout (Lớp 1).

## Week 1 (Session 2) — 2026-08-05
**Tried:** Học kiến thức nền tảng PDF internals, so sánh pdfplumber vs MinerU. Cài đặt MinerU trên Windows, cấu hình model path sang ổ D để tiết kiệm dung lượng ổ C. Viết và chạy Notebook so sánh trích xuất trên 3 test cases: 2 cột, image-only và single-column ([week1_ingestion_learning.md](file:///d:/HocTap/Project_NLP_RAG/clausewise-ai/docs/week1_ingestion_learning.md)). Viết code nền tảng `models.py` và `pdf_reader.py` (Lớp 1) kèm xử lý lỗi image-only (FR-001).
**Result:** Notebook chạy thành công. pdfplumber bị trộn cột (Manulife 2 cột) và trả về 0 ký tự (image-only). MinerU giữ nguyên thứ tự đọc 2 cột chính xác và OCR thành công 25,644 ký tự cho file image-only, mặc dù OCR gặp một số lỗi mất dấu từ khóa cấu trúc (như `DIÊU`, `CHUONG`).
**Reason:** MinerU dùng LayoutLMv3 nhận diện layout giúp giải quyết triệt để bài toán 2 cột. Lỗi OCR dấu tiếng Việt cần được khắc phục ở bước `text_cleaner.py` (Lớp 2).
**Next:** Thực hành Khối 2 (Text Cleaning) thông qua Notebook Experiment 02.

## Week 1 (Session 3) — 2026-08-06
**Tried:** Học Unicode normalization (NFC vs NFD), spacing errors (glyph widths in PDF), và heading wrap. Viết và chạy Notebook thực nghiệm [02_text_cleaning_exploration.py](file:///d:/HocTap/Project_NLP_RAG/clausewise-ai/notebooks/02_text_cleaning_exploration.py) trên file Prudential (trích xuất trang 0-3) và mô phỏng gộp dòng tiêu đề (heading wrap). Lưu kết quả thực nghiệm chi tiết và câu trả lời 4 Acceptance Criteria tại [week1_ingestion_learning_block2.md](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/3cf41de9-e9f2-4571-a96c-91ae0bb4bc7f/week1_ingestion_learning_block2.md).
**Result:** MinerU tự động gộp dòng tiêu đề bị ngắt dòng rất tốt nhờ mô hình Layout. Các lỗi spacing thực tế trong file Prudential (như `ĐI ỀU`) được clean và chuẩn hóa chính xác về `Điều` qua `text_cleaner.py`. Thuật toán gộp dòng tiêu đề (heading wrap) mô phỏng hoạt động chính xác 100%.
**Reason:** Spacing lỗi do font encoding tính sai glyph width và chèn khoảng trắng; NFD tách ký tự thành chữ + dấu tổ hợp làm regex bị fail nên phải chuyển về NFC trước.
**Next:** Thực hành Khối 3 (Chunking strategies) thông qua Notebook Experiment 03.

## Week 1 (Session 4) — 2026-08-06
**Tried:** Nghiên cứu lý thuyết về chiến lược chia nhỏ văn bản (Chunking) và ảnh hưởng của chunk size đến mô hình Embedding và Reranker. Viết và chạy Notebook thực nghiệm [03_chunking_strategies.py](file:///d:/HocTap/Project_NLP_RAG/clausewise-ai/notebooks/03_chunking_strategies.py) để trích xuất và chunk Điều 4 (Giải thích từ ngữ) từ Luật Kinh doanh Bảo hiểm 2022. So sánh giữa fixed-size (500 chars, overlap 50) và clause-aware (chia theo từng khoản/điểm định nghĩa). Lưu câu trả lời 6 Acceptance Criteria của Khối 3 tại [week1_ingestion_learning_block3.md](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/3cf41de9-e9f2-4571-a96c-91ae0bb4bc7f/week1_ingestion_learning_block3.md).
**Result:** Notebook chạy thành công. fixed-size chunking cắt đứt ngữ nghĩa ở cuối mỗi chunk (VD: cắt chữ "rủi ro" thành "rủi" ở chunk 1 và "ro" ở chunk 2, cắt chữ "tái bảo hiểm" thành "tái b" ở chunk 2 và "h nước ngoài" ở chunk 3). Ngược lại, clause-aware chunking trích xuất nguyên vẹn 30 chunk định nghĩa độc lập (độ dài dao động từ 200-500 ký tự), bảo toàn 100% nội dung logic của mỗi điều khoản.
**Reason:** fixed-size chia cắt thuần vật lý không màng ý nghĩa, gây nhiễu cho embedding. Clause-aware sử dụng dấu hiệu cấu trúc tự nhiên để phân vùng ý nghĩa trọn vẹn, không cần overlap mà vẫn giữ được tính liền mạch.
**Next:** Thực hành Khối 3 (Chunking strategies) thông qua Notebook Experiment 03.

## Week 1 (Session 5) — 2026-08-06
**Tried:** Tìm hiểu cách phân biệt Heading thật vs Cross-reference và thuật toán Frequency-based hierarchy inference. Viết và chạy Notebook thực nghiệm [04_heading_detection_regex.py](file:///d:/HocTap/Project_NLP_RAG/clausewise-ai/notebooks/04_heading_detection_regex.py) trên 4 tài liệu: AIA (Roman), Dai-ichi (Article-only), Luật (5 tầng) và Bảo Việt (cross-reference). Lưu câu trả lời 5 Acceptance Criteria của Khối 4 tại [week1_ingestion_learning_block4.md](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/3cf41de9-e9f2-4571-a96c-91ae0bb4bc7f/week1_ingestion_learning_block4.md).
**Result:** 
- Đã sửa Regex để hỗ trợ các ký hiệu markdown headings (`#`, `##`) do MinerU tạo ra.
- Bảo Việt: Đếm được 19 Heading thật và 7 Cross-reference (tại ĐIỀU 2, ĐIỀU 3...). Tỷ lệ False Positive nếu không dùng anchor `^` đầu dòng lên tới **26.92%**.
- Dai-ichi: Thuật toán Frequency-based hierarchy tự động suy luận chính xác phân cấp: `PHAN` (4 lần) -> `DIEU` (22 lần) -> `DECIMAL` (131 lần).
- AIA: Không phát hiện tiêu đề La Mã ở 5 trang đầu vì chúng nằm trong bảng tóm tắt quyền lợi (được bọc trong thẻ `<td>` HTML thay vì đầu dòng) - chứng minh bộ profiler hoạt động đúng khi bỏ qua các tham chiếu tóm tắt trong bảng.
**Reason:** Anchor `^` đầu dòng là điều kiện tiên quyết để lọc bỏ tham chiếu chéo. Thuật toán tần suất hoạt động tốt vì quy luật phân cấp tự nhiên: Chương < Điều < Khoản.
**Next:** Hiện thực hóa mã nguồn Ingestion Pipeline và xử lý các ca biên đặc biệt (HTML Table, Newline Merge, Reset phân cấp).

## Week 1 (Session 6) — 2026-08-06
**Tried:** Viết mã nguồn chính thức cho 4 module: `pdf_reader.py`, `text_cleaner.py`, `structure_profiler.py`, `chunker.py` và `pipeline.py`. Giải quyết 3 ca lỗi layout biên phức tạp:
1. Phẳng hóa tiêu đề gộp trong bảng HTML (cho AIA).
2. Gộp tiêu đề bị gãy làm 2 dòng bằng regex tổng quát cho tất cả các loại Chương, Mục, Phần, Điều, Phụ lục (cho Luật).
3. Reset phân cấp tự động trong Chunker cho các chương không đồng đều (chương có Mục, chương không có Mục).
Viết bộ unit test `tests/ingestion/test_pipeline.py` và cài đặt `pytest` để kiểm chứng.
**Result:** Chạy pytest thành công vượt qua 5/5 bài test tự động.
**Reason:** Giải pháp phẳng hóa và gộp dòng trong Text Cleaner giúp dữ liệu đầu vào sạch tuyệt đối. Thiết kế dọn dẹp cấp con trong Chunker giúp đường dẫn phân cấp `hierarchy_path` luôn chính xác.
**Next:** Chuẩn bị bước vào Week 2: Đánh chỉ mục Vector (Vector Indexing & Storage).




