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

## Week 0 — [19/07/2026]
**Tried:** Setup CI (pytest) cho repo trống, tạo PR đầu tiên qua Git flow

**Result:** CI fail 2 lần trước khi pass — lần 1 do pytest chưa được cài trong workflow, lần 2 do bash `-e` khiến script dừng trước khi kịp kiểm tra exit code của pytest

**Reason:** GitHub Actions chạy mỗi bước `run: |` bằng bash với cờ `-e` mặc định (dừng ngay khi có lệnh trả về mã khác 0) — `pytest; code=$?` không kịp chạy tới phần gán biến trước khi step bị dừng; phải dùng `set +e` trước khi chạy pytest rồi `set -e` lại sau khi đã lấy được exit code

**Next:** Bắt đầu học nội dung Week 0 — Embedding, Semantic Search, Dense/Sparse/Hybrid Retrieval, RAG, Chunking, LoRA/QLoRA cơ bản, các metric đánh giá
