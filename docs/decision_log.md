# Engineering Decision Log

Mỗi quyết định kỹ thuật quan trọng ghi 1 dòng ngay khi quyết định — không đợi đến cuối project.

| Tuần | Quyết định | Các lựa chọn | Kết quả benchmark | Lý do chọn |
|---|---|---|---|---|
| 1 | File `manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf` (image-only, 0 ký tự trích xuất) | (a) Loại khỏi dataset hoàn toàn / (b) Giữ làm test case FR-001 / (c) Đưa vào corpus chính | Không áp dụng — quyết định dựa trên đặc điểm file (0 text layer), không cần benchmark | Chọn (b): giữ lại nhưng KHÔNG đưa vào corpus RAG chính, chỉ dùng làm test case cố định để kiểm tra FR-001 (hệ thống phải phát hiện và từ chối PDF không trích xuất được text, không âm thầm tạo chunk rỗng) |
| 2 | PDF extraction tool (Lớp 1 — layout, reading order, OCR) | (a) pdfplumber / (b) PyMuPDF / (c) Docling (IBM) / (d) MinerU (OpenDataLab) | Không áp dụng — so sánh dựa trên đặc điểm kỹ thuật, chưa benchmark trực tiếp trên dataset | Chọn (d) MinerU: (1) tối ưu multi-column reading order — giải quyết PDF 2 cột Manulife; (2) PaddleOCR tích hợp sẵn hỗ trợ tiếng Việt — cần cho file image-only; (3) semantic coherence loại header/footer/watermark tự động; (4) license Apache 2.0; (5) chạy CPU-only được (~4 GB RAM, pipeline backend). pdfplumber/PyMuPDF bị loại vì không có layout analysis model → lỗi reading order 2 cột. Docling bị loại vì OCR tiếng Việt cần config thêm và 2 cột kém hơn MinerU. Lưu ý: MinerU nằm ngoài tech stack ban đầu (mục 18), đã cập nhật spec. |
| 1 | Ingestion interface: pipeline phụ thuộc PDF xuyên suốt hay tách reader | (a) Pipeline phụ thuộc PDF xuyên suốt (mọi module biết PDF) / (b) Tách PDFReader → ExtractedDocument, downstream format-agnostic | Không áp dụng — quyết định thiết kế, không cần benchmark | Chọn (b): chỉ PDFReader biết MinerU/PDF, các module sau (TextCleaner, StructureProfiler, Chunker) làm việc trên ExtractedDocument — không biết input gốc là PDF hay format khác. MVP chỉ hỗ trợ PDF, không viết thêm reader cho format khác vì chưa có yêu cầu. Nhưng thiết kế này cho phép thêm DocxReader/HtmlReader sau mà không sửa pipeline downstream. Nguyên tắc: không code cho requirement chưa có, nhưng không khóa thiết kế. |

<!--
Ví dụ mẫu (xóa khi có dữ liệu thật):
| 2 | Embedding model | multilingual-e5 vs BGE-M3 | Recall@5: 0.87 vs 0.91 | Chọn BGE-M3 vì dữ liệu tiếng Việt, câu dài |
| 3 | Chunking | Fixed-size vs Clause-aware | MRR: 0.63 vs 0.81 | Chọn Clause-aware, giữ nguyên ngữ cảnh điều khoản |
| 6 | Fine-tuning | Có vs Không | +0.8% chất lượng, chi phí tăng | Không fine-tune, ưu tiên retrieval/reranker |
-->

## ADR (quyết định kiến trúc lớn)

### ADR-002: Hardcoded Parsing vs Document Structure Profiling (DRAFT — chốt chính thức ở Week 2)
**Context:** Task 4/5 (Week 1) đọc tay 16 tài liệu (15 hợp đồng, 5 công ty + Luật KD Bảo hiểm 2022), phát hiện mỗi công ty dùng 1 kiểu cấu trúc phân cấp khác nhau — thậm chí **AIA tự có 3 file thuộc 3 kiểu cấu trúc khác nhau**. Ban đầu cân nhắc "Universal regex" và "Per-source adapter", nhưng cả 2 đều sai hướng gốc: Per-source adapter hardcode theo công ty → không mở rộng được ngoài 5 công ty đã biết (mâu thuẫn trực tiếp với FR-003 — người dùng phải upload được BẤT KỲ hợp đồng nào, kể cả công ty chưa từng thấy); Universal regex cố nhồi mọi pattern vào 1 bộ cố định → dễ vỡ với format lạ.

**Nhận thức đúng:** vấn đề không phải "regex nào đúng", mà là làm sao nhận diện cấu trúc phân cấp của BẤT KỲ tài liệu pháp lý/bảo hiểm tiếng Việt nào — dựa trên quan sát rằng các tài liệu này đều dùng chung 1 bộ từ vựng cấu trúc hữu hạn (Chương/CHƯƠNG → Mục → Điều/ĐIỀU → Khoản → Điểm, hoặc Phần → La Mã → thập phân → chữ cái) do cùng chịu ảnh hưởng quy tắc soạn thảo văn bản pháp luật Việt Nam.

**Cần phân biệt 2 lớp vấn đề khác nhau trong ingestion (quan trọng — 2 lớp cần giải pháp riêng, không loại trừ nhau):**
- Lớp 1 — Extraction quality: trích xuất đúng thứ tự văn bản (giải quyết 2-cột, bảng lớn, phát hiện PDF image-only). Xảy ra TRƯỚC khi có text để phân tích cấu trúc.
- Lớp 2 — Structure understanding: từ text đã sạch, xây dựng cây phân cấp đúng. Đây là phạm vi ADR này.

**Alternatives (cho Lớp 2 — Structure Understanding):**
- A. Universal regex cố định — đã loại, dễ vỡ với format lạ.
- B. Per-source adapter (hardcode theo công ty) — đã loại, không mở rộng được, mâu thuẫn FR-003.
- C. **Document Structure Profiler + Adaptive Chunker** (đề xuất chính) — luồng 3 bước: (1) PROFILE — quét toàn văn bản, đếm & phân loại các heading pattern xuất hiện (dùng bộ từ vựng cấu trúc hữu hạn: Chương, Mục, Điều, Khoản, Điểm, Phần, La Mã, thập phân, chữ cái); (2) BUILD HIERARCHY — từ profile đếm được, tự suy ra thứ tự phân cấp (pattern xuất hiện ít hơn + bao pattern khác thường ở cấp cao hơn); (3) CHUNK — dùng hierarchy vừa xây để tách text, giữ `hierarchy_path` đầy đủ làm metadata mỗi chunk. Phân biệt heading thật vs cross-reference bằng vị trí trong dòng (đầu dòng) + pattern theo sau (có tiêu đề/dấu chấm), không chỉ bằng từ khóa — giải quyết đúng case "nêu tại Điều 2" (Bảo Việt) đã phát hiện ở Week 1.
- D. Layout-aware parsing (Docling) — giải quyết tốt cho Lớp 1 (Extraction quality: 2 cột, bảng, OCR), nhưng không có tri thức về thứ tự ngữ nghĩa riêng của cấu trúc pháp lý Việt Nam (chỉ dựa cỡ chữ, không chắc phân biệt đúng Chương vs Điều nếu độ chênh cỡ chữ nhỏ).

**Decision:** Kết hợp — dùng **MinerU** (pipeline backend, CPU-only) giải quyết Lớp 1 (layout analysis, reading order, OCR tiếng Việt), sau đó chạy **Document Structure Profiler (phương án C)** trên text đã sạch để giải quyết Lớp 2. Đây là kiến trúc 2 tầng, không phải chọn 1 bỏ 1. Xem Decision Log entry Week 2 để biết lý do chọn MinerU thay vì pdfplumber/PyMuPDF/Docling.

**Cần benchmark ở Week 2:**
- Độ chính xác Structure Profiler nhận diện đúng hierarchy trên các case khó nhất đã biết (AIA 3 file khác cấu trúc, Luật 5 tầng).
- Tỷ lệ lọc đúng heading thật vs cross-reference trên tập mẫu có case "nêu tại Điều X" (Bảo Việt).
- Fallback: nếu Profiler không nhận diện đủ tin cậy pattern nào (tài liệu dùng ký hiệu ngoài bộ từ vựng đã biết) → phải báo lỗi rõ ràng, không âm thầm chunk sai (đúng tinh thần Guardrail FR-004 áp dụng cho ingestion).

**Reason:** (điền sau khi có số liệu benchmark)

**Consequences:** (điền sau — dự kiến: Structure Profiler tốn công thiết kế logic profiling/hierarchy-building hơn regex đơn giản, nhưng không cần dependency ngoài, tự chủ hoàn toàn code, và mở rộng được sang tài liệu/công ty chưa từng thấy mà không cần sửa code)
