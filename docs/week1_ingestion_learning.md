# Nhật ký Học tập & Thực nghiệm: Week 1 — Ingestion Parser (MinerU Lớp 1)

## 1. Trả lời 7 Acceptance Criteria (Khối 1: PDF Internals + MinerU)

### AC-1: Vì sao PDF không lưu "paragraph" hay "dòng"?
PDF (Portable Document Format) được thiết kế cho việc in ấn và hiển thị đồng nhất trên mọi thiết bị. Nó không quan tâm đến cấu trúc ngữ nghĩa như "đoạn văn" hay "dòng", mà chỉ lưu các **text objects** (đối tượng văn bản). Mỗi text object chứa một danh sách các ký tự (glyphs), tọa độ hiển thị $(x, y)$, font chữ và kích thước. Việc xuống dòng hay phân đoạn thực chất chỉ là việc đặt các text object tiếp theo ở tọa độ thấp hơn.

### AC-2: Text object trong PDF là gì?
Text object là một lệnh vẽ trong PDF (bắt đầu bằng `BT` và kết thúc bằng `ET`), chứa:
- Tập hợp các ký tự cần hiển thị.
- Toạ độ bắt đầu vẽ trên trang PDF.
- Font chữ, kích thước font, màu sắc và các thuộc tính đồ họa khác.

### AC-3: Coordinate system của PDF?
PDF sử dụng hệ tọa độ Descartes với:
- **Gốc tọa độ (0, 0)** nằm ở góc **dưới-bên-trái** của trang giấy.
- Trục **X** tăng dần từ trái sang phải.
- Trục **Y** tăng dần từ dưới lên trên (y càng lớn thì văn bản càng nằm ở phía trên trang).
- Đơn vị đo là **point** (1 point = 1/72 inch). Trang A4 tiêu chuẩn có kích thước khoảng 595 × 842 points.

### AC-4: Vì sao extraction tuyến tính fail với 2 cột?
Các công cụ trích xuất tuyến tính (như `pdfplumber` hay `PyMuPDF` cơ bản) quét các text objects và sắp xếp chúng theo trục Y (từ trên xuống dưới), sau đó sắp xếp theo trục X (từ trái sang phải) cho những object có cùng tọa độ Y.
Với tài liệu 2 cột, các dòng văn bản ở cột trái và cột phải có cùng tọa độ Y. Công cụ tuyến tính sẽ đọc:
`[Dòng 1 cột trái] + [Dòng 1 cột phải] -> [Dòng 2 cột trái] + [Dòng 2 cột phải] ...`
Hậu quả là trộn lẫn nội dung của hai cột khác nhau thành một chuỗi văn bản vô nghĩa (word salad).

### AC-5: Phân biệt text-layer PDF vs image-only PDF?
- **Text-layer PDF**: Là PDF chứa các text object thực sự. Người dùng có thể bôi đen (select), sao chép (copy) và tìm kiếm (search) văn bản trực tiếp. Trích xuất rất nhanh và chính xác.
- **Image-only PDF**: Là PDF được tạo từ máy quét (scanner) hoặc chụp ảnh lại, không chứa bất kỳ text object nào, chỉ có một hoặc nhiều ảnh raster lớn phủ kín trang. Không thể bôi đen hay copy text layer bằng cách thông thường. Để trích xuất chữ, bắt buộc phải dùng công cụ OCR.

### AC-6: Pipeline MinerU ở mức high-level?
1. **Render**: Chuyển đổi mỗi trang PDF thành ảnh chất lượng cao.
2. **Layout Analysis**: Chạy mô hình học sâu (như LayoutLMv3) trên ảnh trang để phân vùng cấu trúc (nhận diện vùng text, title, table, figure, header, footer).
3. **Reading Order Reconstruction**: Sắp xếp các vùng đã phân loại theo thứ tự đọc tự nhiên (quét hết cột trái từ trên xuống dưới, sau đó chuyển sang cột phải).
4. **Text Extraction**: Trích xuất văn bản (đọc trực tiếp từ text layer nếu có, hoặc dùng PaddleOCR nếu là image-only).
5. **Table Parsing**: Chuyển đổi các vùng bảng biểu thành định dạng cấu trúc HTML.
6. **Output**: Gộp tất cả thành file Markdown sạch và file JSON chi tiết.

### AC-7: OCR hoạt động thế nào ở mức cơ bản?
OCR gồm 2 giai đoạn chính:
1. **Text Detection**: Sử dụng mô hình tích chập (CNN) để phát hiện và vẽ các hộp bao (bounding boxes) quanh các vùng có chứa chữ trên ảnh.
2. **Text Recognition**: Sử dụng mô hình nhận diện (thường kết hợp CNN + RNN + CTC loss hoặc Transformer) để phân tích các pixel chữ trong từng hộp bao và chuyển đổi thành chuỗi ký tự text tương ứng.

---

## 2. Kết quả quan sát thực nghiệm Notebook 01

### 2.1 File 2 cột (`manulife_maxsongkhoe_dieukhoan.pdf`)
- **pdfplumber**: Trộn cột nghiêm trọng. Ở Trang 2, phần giới hạn đồng chi trả ở cột bên phải bị trộn trực tiếp vào giữa câu của Điều 1 ở cột bên trái:
  `...Manulife sẽ chi trả Chi Phí Y Tế Thực Tế Thực Tế phát sinh đầu tiên (cộng dồn) được ghi nhận tương ứng với trong Năm Hợp Đồng...`
- **MinerU**: Trích xuất hoàn toàn chính xác! Nó đọc hết nội dung cột trái (Điều 1. Quyền lợi điều trị nội trú) rồi mới đọc sang cột phải (Giới hạn đồng chi trả). Cấu trúc Markdown đầu ra được định dạng chuẩn với tiêu đề rõ ràng.

### 2.2 File image-only (`manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf`)
- **pdfplumber**: Trích xuất ra **0 ký tự** (Trang trống).
- **MinerU**: Tự động kích hoạt PaddleOCR tiếng Việt. Trích xuất thành công **25,644 ký tự** trên 8 trang.
- **Lỗi OCR phát hiện**:
  - Lỗi mất dấu tiếng Việt và khoảng trắng trong các từ khóa cấu trúc do PaddleOCR chưa tối ưu hoàn toàn font hoặc dấu kết hợp (VD: `DIU KHON SN PHM BO HIM CÁ NHÂN LINH HOT KHÔNG CHIA LÃI`, `NHNG QUY DINH CHUNG`, `DIÊU 1DINH NGHÎA`).
  - Phân văn bản điều khoản bên dưới tuy vẫn bị một số lỗi nhỏ (như `Bên Mua Bo Him`, `Ngưi Đưc Bo Him`), nhưng cấu trúc câu và các phân cấp lớn vẫn được giữ nguyên.
  - *Ý nghĩa:* Điều này khẳng định sự cần thiết của bước **Clean** (`text_cleaner.py`) để sửa lại các từ khóa cấu trúc lớn như `DIÊU` -> `ĐIỀU`, `CHUONG` -> `CHƯƠNG` trước khi chạy bộ Profiler.

### 2.3 File single-column (`daiichilife_anphatdaututhinhvuong_dieukhoan.pdf`)
- **pdfplumber** và **MinerU** đều trích xuất chính xác theo thứ tự đọc tuyến tính từ trên xuống dưới, không có sự xáo trộn văn bản. Điều này xác nhận lỗi trộn văn bản hoàn toàn do layout cột, không phải do pdfplumber bị hỏng ngẫu nhiên.

### 2.4 Cấu trúc đầu ra của MinerU
- Heading được đánh dấu bằng `#` (H1), `##` (H2) rất rõ ràng.
- Các ảnh chụp được tách riêng vào thư mục `images/` và chèn link liên kết `![](images/...)` trong Markdown.
- Bảng biểu được xuất ra dạng bảng text hoặc HTML rất gọn gàng.
- Watermark, header, footer ở đầu và cuối trang bị loại bỏ tự động, làm text cực kỳ sạch.
