# Engineering Decision Log

Mỗi quyết định kỹ thuật quan trọng ghi 1 dòng ngay khi quyết định — không đợi đến cuối project.

| Tuần | Quyết định | Các lựa chọn | Kết quả benchmark | Lý do chọn |
|---|---|---|---|---|
| 1 | File `manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf` (image-only, 0 ký tự trích xuất) | (a) Loại khỏi dataset hoàn toàn / (b) Giữ làm test case FR-001 / (c) Đưa vào corpus chính | Không áp dụng — quyết định dựa trên đặc điểm file (0 text layer), không cần benchmark | Chọn (b): giữ lại nhưng KHÔNG đưa vào corpus RAG chính, chỉ dùng làm test case cố định để kiểm tra FR-001 (hệ thống phải phát hiện và từ chối PDF không trích xuất được text, không âm thầm tạo chunk rỗng) |

<!--
Ví dụ mẫu (xóa khi có dữ liệu thật):
| 2 | Embedding model | multilingual-e5 vs BGE-M3 | Recall@5: 0.87 vs 0.91 | Chọn BGE-M3 vì dữ liệu tiếng Việt, câu dài |
| 3 | Chunking | Fixed-size vs Clause-aware | MRR: 0.63 vs 0.81 | Chọn Clause-aware, giữ nguyên ngữ cảnh điều khoản |
| 6 | Fine-tuning | Có vs Không | +0.8% chất lượng, chi phí tăng | Không fine-tune, ưu tiên retrieval/reranker |
-->

## ADR (quyết định kiến trúc lớn)

### ADR-002: Universal Regex vs Per-Source Adapter Pattern (DRAFT — chốt chính thức ở Week 2)
**Context:** Task 4/5 (Week 1) đọc tay 16 tài liệu (15 hợp đồng, 5 công ty + Luật KD Bảo hiểm 2022), phát hiện mỗi công ty dùng 1 kiểu cấu trúc phân cấp khác nhau:
- AIA: có file dùng Roman (I/II/III/IV) không có "Điều", có file CHƯƠNG không số + Điều liên tục, có file Điều reset theo từng CHƯƠNG.
- Bảo Việt/Prudential: CHƯƠNG → Điều → mục con, nhưng mục lục nhiều lỗi số trang, nhiều cross-reference dễ bị regex heading nhận nhầm.
- Dai-ichi: hầu như không có CHƯƠNG, ĐIỀU là cấp cao nhất.
- Luật: 5 tầng (Chương → Mục → Điều → Khoản → Điểm), sâu hơn mọi hợp đồng công ty.

**Alternatives:**
- A. Universal regex — 1 bộ pattern chung, thử khớp nhiều dạng heading theo thứ tự ưu tiên.
- B. Per-source adapter — mỗi công ty 1 class parser riêng (`AIAParser`, `BaoVietParser`, `DaiichiParser`, `ManulifeParser`, `PrudentialParser`, `LawParser`), cùng kế thừa chung 1 interface `ClauseParser`.

**Decision:** (để trống — quyết định chính thức khi code thật ở Week 2, dựa trên benchmark độ chính xác chunking giữa 2 phương án)

**Reason:** (điền sau khi có số liệu — VD so sánh % chunk đúng ranh giới giữa 2 cách làm trên tập mẫu ≥20 chunk mỗi công ty)

**Consequences:** (điền sau — VD: Per-source adapter dễ đúng hơn nhưng tốn công viết/bảo trì hơn khi thêm công ty mới; Universal regex ít code hơn nhưng rủi ro sai cao hơn với cấu trúc lạ)
