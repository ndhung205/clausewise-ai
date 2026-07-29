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

## Week 1 — [điền ngày]
**Tried:** Thu thập 16 tài liệu (15 hợp đồng từ 5 công ty: AIA, Bảo Việt, Dai-ichi Life, Manulife, Prudential + Luật Kinh doanh Bảo hiểm 2022), đọc tay toàn bộ để phân tích cấu trúc phân cấp (Task 4/5), viết Data Profiling Report đầy đủ
**Result:** Phát hiện mỗi công ty dùng 1 kiểu cấu trúc heading khác nhau (AIA: có file Roman không "Điều", có file Điều reset theo Chương; Dai-ichi: hầu như không có Chương; Bảo Việt/Prudential: có lỗi mục lục/spacing; Luật: 5 tầng phân cấp). Phát hiện 1 file Manulife là PDF image-only (0 ký tự trích xuất được)
**Reason:** Không thể dùng 1 regex cố định (`Điều \d+`) cho toàn bộ dataset vì cấu trúc không đồng nhất giữa các công ty — đây là lý do cần cân nhắc kiến trúc per-source adapter thay vì universal regex (xem ADR-002 draft trong decision_log.md)
**Next:** Bắt đầu Week 2 — Baseline Retrieval System: viết ingestion parser (quyết định chính thức ADR-002), chunking, embedding, Chroma, benchmark Recall@3/5/10
