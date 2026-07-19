# Codex Prompts — ClauseWise AI

Bộ prompt dùng lại mỗi tuần khi làm việc với Codex. Nguyên tắc: Codex chỉ code trong phạm vi 1 tuần, không tự ý mở rộng; mọi số liệu phải tự chạy lại; mọi quyết định phải tự hiểu trước khi merge.

---

## 1. Prompt khởi tạo (dùng 1 lần đầu, hoặc đầu mỗi phiên mới)

```
Đọc kỹ file CLAUSEWISE_PROJECT_SPEC.md trong repo này trước khi làm bất cứ việc gì.
Đây là master spec cho project ClauseWise AI — trợ lý AI phân tích hợp đồng bảo hiểm.

Nguyên tắc bắt buộc khi làm việc với tôi:
1. Chỉ code trong phạm vi tuần tôi yêu cầu — không tự ý làm trước các tuần sau,
   kể cả nếu bạn thấy "tiện làm luôn".
2. Không thêm thư viện/công nghệ ngoài mục 18 (Công cụ) trong spec nếu tôi chưa yêu cầu.
3. Pipeline lõi (retrieve → rerank → build_prompt → call_llm) viết bằng Python thuần,
   không để LangChain che giấu logic bên trong.
4. Sau khi code xong, GIẢI THÍCH ngắn gọn từng phần đã viết — tôi cần tự hiểu,
   không chỉ chạy được.
5. Không tự báo cáo số liệu benchmark — chỉ viết code đo lường, tôi sẽ tự chạy
   và tự xác nhận kết quả.
6. Commit message theo chuẩn mục 15: feat: / fix: / docs: / experiment: / refactor: / chore:

Xác nhận bạn đã đọc và hiểu spec trước khi tôi giao việc tuần đầu tiên.
```

---

## 2. Prompt giao việc theo tuần (đổi số tuần + nội dung mỗi lần)

```
Làm Week [X] theo đúng mục 7 (Roadmap) và Definition of Done tương ứng
trong docs/roadmap.md của CLAUSEWISE_PROJECT_SPEC.md.

Functional Requirements liên quan tuần này: [FR-XXX, FR-XXX]

Chỉ làm đúng Deliverable của tuần này, dừng lại sau khi xong — không tự chạy
tiếp sang tuần sau dù còn thời gian/context.

Sau khi code xong:
- Liệt kê các file đã tạo/sửa và vai trò từng file
- Giải thích các quyết định kỹ thuật quan trọng đã đưa ra trong lúc code
  (nếu có, để tôi ghi vào Decision Log)
- Chỉ ra lệnh cụ thể để tôi tự chạy benchmark/test, không tự báo số liệu
```

---

## 3. Prompt yêu cầu giải thích (dùng sau khi Codex code xong, trước khi merge)

```
Giải thích chi tiết đoạn code [tên file/hàm cụ thể] này:
- Nó giải quyết vấn đề gì trong pipeline
- Vì sao chọn cách làm này (nếu có alternative, so sánh ưu nhược điểm)
- Nếu tôi đổi [tham số/thư viện/config] thì hành vi sẽ khác thế nào

Giải thích như đang dạy tôi, không chỉ mô tả code làm gì theo từng dòng.
```

---

## 4. Prompt xác minh benchmark (dùng khi có số liệu)

```
Tôi vừa tự chạy benchmark, kết quả là: [dán kết quả thật]

So sánh với mục tiêu Acceptance Criteria trong FR liên quan (spec mục 2).
Nếu chưa đạt, đề xuất 2-3 hướng cải thiện cụ thể — không tự sửa code ngay,
chỉ đề xuất để tôi quyết định hướng nào trước.
```

---

## 5. Prompt trước khi qua tuần mới (checklist tự kiểm tra)

```
Trước khi tôi báo "xong Week [X]", hãy liệt kê lại toàn bộ Definition of Done
của tuần này từ docs/roadmap.md, đánh dấu mục nào đã có bằng chứng cụ thể
(file, số liệu, output thật) và mục nào tôi có thể đang tự nhận "xong" mà
chưa có bằng chứng.
```

---

## Lưu ý khi dùng

- Không paste nguyên cả 11 tuần vào 1 lần yêu cầu — luôn dùng Prompt #2 riêng cho từng tuần.
- Sau mỗi tuần, tự viết Journal (mục 13 spec) bằng lời của mình, không copy nguyên văn giải thích của Codex.
- Nếu không tự giải thích lại được phần Codex vừa làm, coi như tuần đó **chưa đạt DoD thật**, dù code chạy đúng.
