# Dataset

Trạng thái: Week 1 - Data Collection & Profiling.

## Phạm vi Week 1 - chỉ dừng ở đây

Mục tiêu duy nhất: thu thập dữ liệu thô, hiểu cấu trúc tài liệu, ghi nhận rủi ro extraction/chunking và chuẩn bị cho ingestion.

Không làm trong file này: embedding, Chroma, BM25, RAG, reranker, LangChain, fine-tune.

## 1. Nguồn dữ liệu

Dataset hiện có gồm 15 file quy tắc/điều khoản sản phẩm bảo hiểm và 1 văn bản luật.

| Nhóm | Nguồn | File |
|---|---|---|
| Hợp đồng/quy tắc bảo hiểm | AIA Việt Nam | `data/raw/contracts/aia_*.pdf` |
| Hợp đồng/quy tắc bảo hiểm | Bảo Việt Nhân thọ | `data/raw/contracts/baoviet_*.pdf` |
| Hợp đồng/quy tắc bảo hiểm | Dai-ichi Life Việt Nam | `data/raw/contracts/daiichilife_*.pdf` |
| Hợp đồng/quy tắc bảo hiểm | Manulife Việt Nam | `data/raw/contracts/manulife_*.pdf` |
| Hợp đồng/quy tắc bảo hiểm | Prudential Việt Nam | `data/raw/contracts/prudential_*.pdf` |
| Văn bản luật | Luật Kinh doanh Bảo hiểm 2022 | `data/raw/laws/luat_kinhdoanh_baohiem_2022_08qh15.pdf` |

Lưu ý governance: dữ liệu được dùng cho mục đích học tập/phi thương mại. Khi có thời gian, cần bổ sung URL gốc chính xác của từng PDF vào bảng governance để tăng tính tái lập.

## 2. Số lượng file

| Loại | Số lượng |
|---|---:|
| Hợp đồng/quy tắc bảo hiểm | 15 |
| Văn bản luật | 1 |
| FAQ | 0 |
| Tổng PDF | 16 |

## 3. Data Profiling

| Chỉ số | Giá trị |
|---|---:|
| Số PDF | 16 |
| Tổng số trang | 471 |
| Số điều khoản (ước lượng theo số lần match `Điều/ĐIỀU`) | 1,190 |
| Số sản phẩm bảo hiểm | 15 |
| Số công ty bảo hiểm | 5 |
| Số văn bản luật | 1 |

Ghi chú: số điều khoản ở trên là số lần match heading/cross-reference trong text extraction, chưa dedupe mục lục và các dòng nhắc lại như "nêu tại Điều X". Con số này chỉ dùng để profiling thô, không phải benchmark.

## 4. Danh sách tài liệu đã thu thập

| File | Nhóm | Số trang | Text layer | Ghi chú nhanh |
|---|---|---:|---|---|
| `data/raw/contracts/aia_anbinhuuviet_dieukhoan.pdf` | AIA | 10 | Có | Cấu trúc mục lớn bằng Roman `I/II/III/IV`, không thấy heading `Điều` trong mục lục/trang đầu. |
| `data/raw/contracts/aia_khoetronven_dieukhoan.pdf` | AIA | 28 | Có | `CHƯƠNG` không đánh số + `Điều`, có lỗi spacing/ký tự rơi nhẹ. |
| `data/raw/contracts/aia_suckhoetrondoi_dieukhoan.pdf` | AIA | 26 | Có | `Điều` reset theo từng `CHƯƠNG`, có bảng quyền lợi lớn. |
| `data/raw/contracts/baoviet_honhop-anlocvungben_dieukhoan.pdf` | Bảo Việt | 32 | Có | Có trang tóm tắt trước mục lục, cấu trúc `Chương -> Điều -> 8.1/a)`. |
| `data/raw/contracts/baoviet_lienketchung-tamhoachdinh_dieukhoan.pdf` | Bảo Việt | 40 | Có | Nhiều mục con decimal, có phần quỹ liên kết chung. |
| `data/raw/contracts/baoviet_lifecare2_dieukhoan.pdf` | Bảo Việt | 32 | Có | Có thời gian chờ/loại trừ nổi bật, nhiều cross-reference tới Điều khác. |
| `data/raw/contracts/daiichilife_anphatdaututhinhvuong_dieukhoan.pdf` | Dai-ichi Life | 38 | Có | Top-level chủ yếu là `ĐIỀU`, bên dưới là `2.1/2.2/...`. |
| `data/raw/contracts/daiichilife_chamsocdieutrisautainan247_dieukhoan.pdf` | Dai-ichi Life | 16 | Có | Có nhiều định nghĩa `1.x` và danh sách Roman `i/ii/iii`. |
| `data/raw/contracts/daiichilife_vungbuocvuonxa_dieukhoan.pdf` | Dai-ichi Life | 22 | Có | `ĐIỀU -> 2.1/2.2`, heading dài có thể bị wrap dòng. |
| `data/raw/contracts/manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf` | Manulife | 8 | Không | Text extraction trả 0 ký tự; render thấy chữ, khả năng image-only/scan. |
| `data/raw/contracts/manulife_hon-hop-giao-duc-tich-hop-benh-ly-nghiem-trong_dieukhoan.pdf` | Manulife | 20 | Có | Layout 2 cột rõ, extraction tuyến tính làm trộn thứ tự khoản. |
| `data/raw/contracts/manulife_maxsongkhoe_dieukhoan.pdf` | Manulife | 19 | Có | Layout 2 cột, nhiều bảng/bullet, có `Chương 1:` và `ĐIỀU 1.`. |
| `data/raw/contracts/prudential_pru-bao-ve-toi-da2-tnc_dieukhoan.pdf` | Prudential | 38 | Có | Chủ yếu theo `Điều`, có lỗi spacing tiếng Việt trong text extraction. |
| `data/raw/contracts/prudential_pru-dau-tu-vung-tien-tnc_dieukhoan.pdf` | Prudential | 47 | Có | `CHƯƠNG -> Điều`, mục lục có số trang bị tách như `2. 0`, `2..6.`. |
| `data/raw/contracts/prudential_yen-tam-vui-khoe-tnc_dieukhoan.pdf` | Prudential | 24 | Có | `CHƯƠNG -> Điều`, nhiều heading dài bị xuống dòng. |
| `data/raw/laws/luat_kinhdoanh_baohiem_2022_08qh15.pdf` | Luật | 71 | Có | Cấu trúc sâu `Chương -> Mục -> Điều -> Khoản -> Điểm`. |

## 5. Đặc điểm tài liệu theo công ty

### AIA

- `aia_anbinhuuviet_dieukhoan.pdf` dùng mục lớn dạng Roman: `I. Quyền lợi bảo hiểm`, `II. Những lưu ý khi tham gia bảo hiểm`, `III. Giải quyết quyền lợi bảo hiểm`, `IV. Những điều khoản chung`. Vì không thấy cấu trúc `Điều`, chunking cần hỗ trợ section Roman.
- `aia_khoetronven_dieukhoan.pdf` có `CHƯƠNG` không đánh số và `Điều` đánh số liên tục. Parser không nên yêu cầu chương phải có `I/II/III`.
- `aia_suckhoetrondoi_dieukhoan.pdf` có `Điều` reset lại từ 1 trong từng chương. Chunk ID phải gồm đầy đủ parent path, ví dụ `CHƯƠNG NHỮNG LƯU Ý... / Điều 7`, tránh trùng với `Điều 7` ở chương khác.
- Có bảng quyền lợi/hạn mức lớn. Nếu chuyển bảng thành text phẳng, nguy cơ mất quan hệ giữa chương trình bảo hiểm, hạn mức, điều kiện áp dụng.

### Bảo Việt

- Cả 3 file đều có phần tóm tắt/lưu ý trước mục lục. Các dòng như `1. Quyền lợi của sản phẩm`, `2. Bảo hiểm tạm thời` xuất hiện trước nội dung chính, dễ bị nhận nhầm là heading cần chunk.
- Cấu trúc chính thường là `CHƯƠNG I -> Điều -> mục con decimal -> điểm a)`.
- Có nhiều dòng cross-reference như "nêu tại Điều 24", "tại Chương I"; regex heading cần phân biệt dòng heading thật với tham chiếu trong câu.
- Có watermark/mã tài liệu lặp lại ở một số trang, cần lọc khỏi text trước khi chunk.

### Dai-ichi Life

- Cấu trúc thường không có `CHƯƠNG`; top-level là `ĐIỀU 1`, `ĐIỀU 2`, bên dưới là `1.1`, `1.2`, `2.1`, `2.2`.
- Một số file có danh sách con bằng Roman `i.`, `ii.`, `iii.` trong định nghĩa hoặc điều kiện bệnh viện/y tế.
- Heading dài trong mục lục có thể bị wrap sang dòng tiếp theo. Parser cần nối dòng heading bị gãy trước khi nhận diện.
- Không nên chỉ chunk theo `Điều`, vì các điều định nghĩa dài chứa nhiều mục con khác nhau.

### Manulife

- `manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf` là rủi ro lớn nhất: text layer rỗng dù ảnh render có chữ. FR-001 yêu cầu phát hiện PDF scan/image-only và báo lỗi rõ, không tạo kết quả rỗng.
- `manulife_hon-hop-giao-duc-tich-hop-benh-ly-nghiem-trong_dieukhoan.pdf` và `manulife_maxsongkhoe_dieukhoan.pdf` dùng layout 2 cột. Extraction mặc định theo tọa độ tuyến tính có thể trộn thứ tự trái/phải, ví dụ `1.1`, `1.4`, `1.2`, `1.5`.
- Có nhiều cấp `CHƯƠNG`, `ĐIỀU`, `1.1`, `1.7.1`, `a)`, `i)`, bullet. Cần column-aware extraction trước rồi mới chạy regex clause-aware.
- Một số bảng/quyền lợi có thể cần giữ dạng text có cấu trúc thay vì nối dòng tự do.

### Prudential

- `prudential_pru-bao-ve-toi-da2-tnc_dieukhoan.pdf` chủ yếu theo `Điều`, không thấy `Chương` rõ trong mục lục chính.
- `prudential_pru-dau-tu-vung-tien-tnc_dieukhoan.pdf` và `prudential_yen-tam-vui-khoe-tnc_dieukhoan.pdf` dùng `CHƯƠNG -> Điều`.
- Text extraction có lỗi spacing trong tiếng Việt, ví dụ `MỤC L ỤC`, `Điều Kho ản`, `Giá Tr ị`. Preprocessing cần normalize khoảng trắng bất thường nhưng không làm mất dấu tiếng Việt.
- Mục lục có số trang bị tách/chèn dấu, ví dụ `2. 0`, `2..6.`, `4. 2`; không nên dùng số cuối dòng mục lục làm nội dung chunk.

### Luật Kinh doanh Bảo hiểm 2022

- Cấu trúc sâu nhất trong dataset: `Chương -> Mục -> Điều -> Khoản -> Điểm a/b/c`.
- Nếu chỉ chunk tới cấp `Điều`, các điều dài như phần giải thích từ ngữ hoặc điều cấm/gian lận sẽ quá lớn và lẫn nhiều ý nhỏ.
- Cần giữ đường dẫn phân cấp đầy đủ trong metadata, ví dụ `Chương I / Điều 4 / Khoản 1`, để citation sau này đủ rõ.

### Bảng tổng hợp đặc điểm cấu trúc

Bảng này giúp nhìn tổng quan sự đa dạng của dataset — lưu ý rằng đặc điểm gắn với **tài liệu**, không phải công ty (AIA tự có 3 file với 3 kiểu cấu trúc khác nhau).

| Đặc điểm | AIA | Bảo Việt | Dai-ichi | Manulife | Prudential | Luật |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Roman section (I/II/III) | ✓ | | | | | |
| Chương / CHƯƠNG | ✓ | ✓ | | ✓ | ✓ | ✓ |
| Điều / ĐIỀU | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mục con decimal (1.1, 1.2) | | ✓ | ✓ | ✓ | | ✓ |
| Layout 2 cột | | | | ✓ | | |
| PDF image-only (cần OCR) | | | | ✓ | | |
| Bảng quyền lợi lớn | ✓ | | | ✓ | | |
| Phân cấp sâu (≥5 tầng) | | | | | | ✓ |
| Lỗi spacing/ký tự | ✓ | | | | ✓ | |
| Điều reset theo Chương | ✓ | | | | | |

## 6. Khó khăn gặp phải

- Không đồng nhất cấu trúc giữa các **tài liệu** — kể cả trong cùng 1 công ty (AIA tự có 3 file với 3 kiểu cấu trúc khác nhau). Điều này chứng minh **company ≠ document structure**, là lập luận chính cho Document Structure Profiler thay vì per-company parser (xem ADR-002).
- Layout 2 cột (hiện gặp ở Manulife, có thể gặp ở bất kỳ tài liệu bảo hiểm nào) làm sai thứ tự text nếu dùng extraction mặc định.
- Có PDF image-only/scan: `manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf`.
- Bảng quyền lợi lớn xuất hiện trong một số tài liệu (hiện gặp ở AIA/Manulife); cần table-aware hoặc ít nhất giữ block bảng cùng metadata.
- Mục lục, trang tóm tắt, watermark, footer/header và mã tài liệu có thể gây nhiễu regex.
- Text extraction có lỗi spacing/ký tự rơi (hiện gặp ở Prudential và AIA).
- Các danh sách con `a)`, `i.`, `i)` chứa chi tiết quan trọng; không nên bỏ qua khi chunk.

## 7. Phát hiện phục vụ thiết kế ingestion Week 2

Các quan sát dưới đây mô tả **đặc điểm tài liệu**, không phải thiết kế parser. Ingestion system hoạt động theo document profile (xem ADR-002), không hardcode theo công ty.

### 7.1 Yêu cầu extraction (Lớp 1 — trước khi có text)

- Kiểm tra file PDF hợp lệ và text layer. Nếu text rỗng hoặc quá ít ký tự/trang → báo lỗi PDF scan/image-only theo FR-001.
- Phân loại layout: single-column, two-column, table-heavy. Với tài liệu 2 cột, cần column-aware extraction (MinerU) trước khi nối dòng.
- Làm sạch text: loại header/footer/watermark/mã tài liệu lặp, normalize spacing bất thường, nối heading bị wrap.

### 7.2 Yêu cầu structure profiling (Lớp 2 — từ text đã sạch)

Document Structure Profiler cần nhận diện các profile sau (phân loại theo **đặc điểm tài liệu**, không theo công ty):

| Profile | Đặc điểm cấu trúc | Ví dụ tài liệu đã gặp |
|---|---|---|
| Roman top-level | Mục lớn dạng `I/II/III/IV`, không có `Điều` | `aia_anbinhuuviet` |
| Chapter → Article (reset) | `CHƯƠNG` + `Điều` reset từ 1 trong mỗi chương | `aia_suckhoetrondoi` |
| Chapter → Article (continuous) | `CHƯƠNG` → `Điều` đánh số liên tục | `baoviet_*`, `prudential_*`, `manulife_maxsongkhoe` |
| Article top-level | Không có `CHƯƠNG`, `ĐIỀU` là cấp cao nhất → decimal sub | `daiichilife_*` |
| Deep hierarchy (law) | `Chương → Mục → Điều → Khoản → Điểm` (5 tầng) | `luat_kinhdoanh_baohiem_2022` |

Profiler cần output `hierarchy_confidence` — nếu confidence thấp (không nhận diện đủ tin cậy pattern nào) → reject rõ ràng, không âm thầm chunk sai (FR-004).

### 7.3 Metadata tối thiểu mỗi chunk

| Field | Mô tả | Ví dụ |
|---|---|---|
| `source_file` | Tên file gốc | `aia_suckhoetrondoi_dieukhoan.pdf` |
| `company` | Công ty (extract từ filename) | `aia` |
| `product` | Sản phẩm | `suckhoetrondoi` |
| `document_type` | Loại tài liệu | `contract` / `law` |
| `page_start` | Trang bắt đầu | `2` |
| `page_end` | Trang kết thúc | `3` |
| `hierarchy_path` | Đường dẫn phân cấp đầy đủ | `CHƯƠNG I / Điều 3 / 3.1` |
| `section` | Heading gần nhất | `Điều 3. Quyền lợi bảo hiểm` |
| `extractor` | Tool extraction Lớp 1 | `mineru` |
| `profile_type` | Profile structure đã nhận diện | `chapter_article_reset` |
| `hierarchy_confidence` | Độ tin cậy profiling | `0.94` |
| `ocr_used` | Có dùng OCR không | `true` / `false` |
| `parser_version` | Phiên bản parser | `0.1.0` |

### 7.4 Kiểm tra đầu ra

In mẫu ít nhất 20 chunk để kiểm tra bằng mắt theo DoD Week 2 (chunk không cắt giữa 1 điều khoản).

## 8. Data Governance

Ngày kiểm kê: 2026-07-28.

| File | Nguồn | Ngày tải / Xác nhận cuối | License/Điều kiện sử dụng | SHA256 |
|---|---|---|---|---|
| `data/raw/contracts/aia_anbinhuuviet_dieukhoan.pdf` | Website công khai AIA Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `c81af866c216896bd4150e213dbcbd3c400f1f77449557fe5e5f718b8d720a41` |
| `data/raw/contracts/aia_khoetronven_dieukhoan.pdf` | Website công khai AIA Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `d635de929b95459c35465602fc42a5192bbea9962cd7c0acc6281050aca7abc3` |
| `data/raw/contracts/aia_suckhoetrondoi_dieukhoan.pdf` | Website công khai AIA Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `d09c590df58c784d677a1ed61c589a7b50c4bfe915c248f191d3ec8a524fa589` |
| `data/raw/contracts/baoviet_honhop-anlocvungben_dieukhoan.pdf` | Website công khai Bảo Việt Nhân thọ | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `557d2190441835444474ba87b330ea9da5060319e3e7c3dc17e15763a016607b` |
| `data/raw/contracts/baoviet_lienketchung-tamhoachdinh_dieukhoan.pdf` | Website công khai Bảo Việt Nhân thọ | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `9403f02b4b0658ad4584677bb20f008ce03fc3fdbf52d5b9871e4b7b7674d691` |
| `data/raw/contracts/baoviet_lifecare2_dieukhoan.pdf` | Website công khai Bảo Việt Nhân thọ | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `83093a5ecb3c1559acc35b2aa6272ebdc34a24500b0e0dcfb24f55bf4074de52` |
| `data/raw/contracts/daiichilife_anphatdaututhinhvuong_dieukhoan.pdf` | Website công khai Dai-ichi Life Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `d159ba5f89bccdb687cd085444c88171c335e1200c5473ed85b3833ec5cab290` |
| `data/raw/contracts/daiichilife_chamsocdieutrisautainan247_dieukhoan.pdf` | Website công khai Dai-ichi Life Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `6229eebd7bc3915547279a19ff523b3e2fd6e69134e7111ad1950535fd633cf1` |
| `data/raw/contracts/daiichilife_vungbuocvuonxa_dieukhoan.pdf` | Website công khai Dai-ichi Life Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `9aa9f0f4fc7ef5b6e2d63df7e0d2ac9f06c70d5cfbf794d47650352905f02000` |
| `data/raw/contracts/manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf` | Website công khai Manulife Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `7d31583154415d3c19a86a69a5e8f1584286b23f4885f7d549afd58a495260c1` |
| `data/raw/contracts/manulife_hon-hop-giao-duc-tich-hop-benh-ly-nghiem-trong_dieukhoan.pdf` | Website công khai Manulife Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `383aaf95dfed027cc8faaf1ace455fb1bdfecc1efb515c2d7189e506bc54b409` |
| `data/raw/contracts/manulife_maxsongkhoe_dieukhoan.pdf` | Website công khai Manulife Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `e2cd64c6953818159b003cfb5a6712e012cbf765aa4ee8208a853b32ef73f137` |
| `data/raw/contracts/prudential_pru-bao-ve-toi-da2-tnc_dieukhoan.pdf` | Website công khai Prudential Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `a61b6fe1351eb3810b5a3be85309f2c72b6ab1226e9038dcba103c702c69b207` |
| `data/raw/contracts/prudential_pru-dau-tu-vung-tien-tnc_dieukhoan.pdf` | Website công khai Prudential Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `d5cedaad53b3ebb98b54184a49c8bfaa33a936dd51b3bef6cec5b48ed4467c5e` |
| `data/raw/contracts/prudential_yen-tam-vui-khoe-tnc_dieukhoan.pdf` | Website công khai Prudential Việt Nam | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `2df4908f7024e90ce77d6838e58b08f863ff7055958c6d497d998cf2427bfb4d` |
| `data/raw/laws/luat_kinhdoanh_baohiem_2022_08qh15.pdf` | Văn bản pháp luật công khai | 2026-07-28 | Chỉ dùng học tập/phi thương mại; cần bổ sung URL gốc | `dacf2f1b435f3cac1b848140fe2ad1a1939c3419c29dc438e95622ca01548a0e` |

## 9. Việc còn thiếu trước khi chốt Week 1

- Bổ sung URL gốc chính xác của từng PDF vào bảng governance nếu còn lưu lại lịch sử tải.
- Quyết định có giữ `manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf` trong dataset v1 hay chỉ dùng nó làm negative case cho scan/image-only detection.
