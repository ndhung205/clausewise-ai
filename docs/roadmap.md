# Roadmap — ClauseWise AI

Nguyên tắc xuyên suốt:
1. Không thêm công nghệ nếu chưa có benchmark chứng minh cần thiết.
2. Không chuyển sang tuần mới nếu Deliverable + Definition of Done (DoD) của tuần hiện tại chưa đạt.
3. Viết tài liệu ngay khi làm (Journal, Decision Log), không viết lại từ trí nhớ ở cuối.

---

## Week 0 — Foundations
**Milestone:** Hiểu nền tảng RAG/Retrieval trước khi code
**Deliverable:** Note giải thích RAG bằng sơ đồ tự vẽ (embedding, dense/sparse/hybrid retrieval, ANN)
**DoD:**
- [ ] Giải thích được RAG khác gì hỏi thẳng LLM, không cần nhìn tài liệu
- [ ] Giải thích được BM25 vs Embedding vs Hybrid
**Time Budget:** ~10h (đọc + note)
**Risk:** —

## Week 1 — Data Collection & Profiling
**Milestone:** Dataset v1 sẵn sàng, đã chunk theo điều khoản
**Deliverable:** `data/raw/` đầy đủ + Data Profiling Report (`docs/dataset.md`)
**DoD:**
- [ ] Có ≥15 hợp đồng/tài liệu bảo hiểm + luật liên quan
- [ ] Clause-aware chunking chạy được, in ra mẫu kiểm tra bằng mắt
- [ ] Profiling: số PDF, số trang, số điều khoản, số sản phẩm/công ty
**Time Budget:** ~16h
**Risk:** PDF quét kém chất lượng → OCR lỗi → phương án: ưu tiên nguồn có bản text-first

## Week 2 — Baseline Retrieval System
**Milestone:** RAG chạy được end-to-end
**Deliverable:** RAG baseline + Benchmark Report v1
**DoD:**
- [ ] Upload tài liệu → hỏi đáp được qua Streamlit demo
- [ ] Benchmark Recall@3/5/10, MRR, Latency trên ≥20 câu test
- [ ] Benchmark chạy lại được bằng 1 lệnh (`python -m src.evaluation.run_benchmark`)
**Time Budget:** ~18h
**Risk:** Retrieval kém ngay từ đầu → benchmark chunking trước khi đổ lỗi cho embedding

## Week 3 — Retrieval Optimization
**Milestone:** Cải thiện retrieval bằng reranker + query rewrite + phân loại ý định câu hỏi
**Deliverable:** Retrieval v2 + Reranker/Query Rewrite Report + Query Intent Classification Report (FR-006)
**DoD:**
- [ ] Tích hợp cross-encoder reranker (pretrained)
- [ ] Query rewrite bằng LLM trước khi retrieve
- [ ] So sánh Recall@5 trước/sau — có số liệu rõ ràng
- [ ] Guardrail: từ chối trả lời khi confidence thấp
- [ ] Query Intent Classification: test ≥15 câu mỗi nhóm (đủ ngữ cảnh / thiếu ngữ cảnh / ngoài phạm vi / xin khuyến nghị / gian lận-injection), đạt ≥85% phân loại đúng, ≥95% precision cho nhóm gian lận/injection
- [ ] (Stretch, không bắt buộc) Benchmark Parent-Child Retrieval và/hoặc Contextual Retrieval nếu còn thời gian — ghi kết quả vào Decision Log dù dùng hay không dùng
**Time Budget:** ~18h
**Risk:** —

## Week 4 — Risk Analysis Engine
**Milestone:** Policy Risk Scanner hoạt động
**Deliverable:** Demo Policy Risk Scanner (rule-based + LLM hybrid)
**DoD:**
- [ ] Upload hợp đồng → tự động gắn nhãn: quyền lợi chính / cần chú ý / dễ bị từ chối / thời gian chờ
- [ ] Phần "chắc chắn" xử lý bằng rule, phần "cần suy luận" xử lý bằng LLM
- [ ] Test trên ≥3 hợp đồng khác nhau
**Time Budget:** ~18h
**Risk:** —

## Week 5 — Evaluation Dataset Construction
**Milestone:** Bộ dữ liệu đánh giá có cấu trúc
**Deliverable:** Synthetic QA Dataset v1 (`data/synthetic_qa/`)
**DoD:**
- [ ] ≥500 cặp Q&A theo schema: question, answer, evidence, page, section, company, product, difficulty, question_type
- [ ] Kiểm tra thủ công ≥10% mẫu để đảm bảo chất lượng
**Time Budget:** ~14h
**Risk:** Dataset ít → sinh thêm synthetic QA có kiểm soát chất lượng

## Week 6 — Model Adaptation Decision
**Milestone:** Quyết định có fine-tune hay không, dựa trên benchmark
**Deliverable:** Fine-tune Report HOẶC Decision Report (không fine-tune)
**DoD:**
- [ ] Có số liệu benchmark rõ ràng làm căn cứ quyết định
- [ ] Nếu fine-tune: log đầy đủ qua MLflow, so sánh trước/sau
- [ ] Quyết định (làm hoặc không làm) được ghi vào Decision Log kèm lý do
**Time Budget:** ~16-20h (tùy có fine-tune hay không)
**Risk:** GPU hết quota → hoãn/bỏ fine-tune, ưu tiên giữ benchmark

## Week 7 — Deployment Infrastructure
**Milestone:** Hệ thống chạy được qua Docker + API
**Deliverable:** Docker + FastAPI + MLflow logging
**DoD:**
- [ ] `docker run` chạy được trên máy khác (nhờ người khác test)
- [ ] API trả kết quả đúng qua Postman/curl
- [ ] MLflow log các lần thử nghiệm chính
- [ ] Dashboard log latency, confidence, no-answer rate
**Time Budget:** ~16h
**Risk:** Không đủ thời gian → bỏ tracing nâng cao (LangSmith/OpenTelemetry), giữ MLflow cơ bản

## Week 8 — UI Beta
**Milestone:** Giao diện demo chạy được
**Deliverable:** UI Beta
**DoD:**
- [ ] Người ngoài dùng thử được không cần hướng dẫn
**Time Budget:** ~14h
**Risk:** —

## Week 9 — UI Final + Testing
**Milestone:** Hoàn thiện + có test
**Deliverable:** UI Final + test suite cơ bản
**DoD:**
- [ ] Test cho retrieval, evaluation, api, risk_scanner (mỗi phần ≥1 test)
- [ ] Xử lý các edge case chính (câu hỏi ngoài phạm vi, tài liệu lỗi...)
**Time Budget:** ~16h
**Risk:** —

## Week 10 — Documentation & Release
**Milestone:** Sản phẩm hoàn chỉnh, có thể show
**Deliverable:** README hoàn chỉnh + Blog/Case Study + Video Demo
**DoD:**
- [ ] README không còn mục TODO
- [ ] Video demo ≤2 phút
- [ ] Deploy public (HuggingFace Spaces/Render)
- [ ] Decision Log, Benchmark, Dataset docs đầy đủ
**Time Budget:** ~14h
**Risk:** —

## Week 11 — Failure Analysis
**Milestone:** Phân tích lỗi có hệ thống
**Deliverable:** Error Analysis Report
**DoD:**
- [ ] Lấy ≥200 câu test, phân loại lỗi: Retrieval Failure / Citation Error / Unsupported Claim / Prompt / Model
- [ ] Có biểu đồ phân bố lỗi
- [ ] Đề xuất cải thiện tiếp theo nếu có thêm thời gian
**Time Budget:** ~12h
**Risk:** —

---

## Quy ước Time Budget
Nếu 1 tuần vượt quá **20 giờ**, cắt bỏ phần stretch goal (không nằm trong DoD) để giữ tiến độ, ghi lại lý do vào `journal.md`.
