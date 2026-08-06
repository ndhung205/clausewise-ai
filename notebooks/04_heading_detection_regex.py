"""
Notebook Experiment 04: Regex Heading Detection & Document Structure Profiling
================================================================================
Mục tiêu:
  1. Viết regex cho từng pattern type (Chương, Điều, Khoản, Điểm, Roman, Decimal).
  2. Chạy trên 3 file đại diện: AIA (Roman), Dai-ichi (Article-only), Luật (5 tầng).
  3. Đếm heading thật vs cross-reference trên file Bảo Việt → tính false positive rate.
  4. Thử thuật toán Frequency-based hierarchy để tự suy luận phân cấp.

Chạy:
  $env:PYTHONPATH="d:\HocTap\Project_NLP_RAG\clausewise-ai"; $env:PYTHONIOENCODING="utf-8"; python notebooks/04_heading_detection_regex.py
"""

import re
import subprocess
from pathlib import Path

from src.ingestion.text_cleaner import clean_text_content

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "extraction_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AIA_PDF = DATA_DIR / "contracts" / "aia_anbinhuuviet_dieukhoan.pdf"
BAOVIET_PDF = DATA_DIR / "contracts" / "baoviet_lifecare2_dieukhoan.pdf"
DAIICHI_MD = (
    OUTPUT_DIR
    / "mineru_single_column"
    / "daiichilife_anphatdaututhinhvuong_dieukhoan"
    / "auto"
    / "daiichilife_anphatdaututhinhvuong_dieukhoan.md"
)
LAW_MD = (
    OUTPUT_DIR
    / "mineru_law_pages"
    / "luat_kinhdoanh_baohiem_2022_08qh15"
    / "auto"
    / "luat_kinhdoanh_baohiem_2022_08qh15.md"
)

results = []


# ==============================================================================
# Helper: Gọi MinerU trích xuất nhanh vài trang đầu
# ==============================================================================


def run_quick_extraction(
    pdf_path: Path, out_name: str, start_page: int = 0, end_page: int = 4
) -> str:
    """Gọi MinerU trích xuất nhanh 5 trang đầu của PDF."""
    print(f" Đang chạy MinerU trên {pdf_path.name} (trang {start_page} đến {end_page})...")
    out_dir = OUTPUT_DIR / out_name

    cmd = [
        "mineru",
        "-p",
        str(pdf_path),
        "-o",
        str(out_dir),
        "-s",
        str(start_page),
        "-e",
        str(end_page),
        "--method",
        "auto",
        "--backend",
        "pipeline",
    ]

    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=300)
    if result.returncode != 0:
        print("❌ Lỗi MinerU:", result.stderr[:300])
        return ""

    md_files = list(out_dir.rglob("*.md"))
    if not md_files:
        print("❌ Không tìm thấy markdown output")
        return ""

    raw_text = md_files[0].read_text(encoding="utf-8")
    return clean_text_content(raw_text)


# ==============================================================================
# PHẦN 1: Định nghĩa các Regex Patterns cho các cấp Tiêu đề
# ==============================================================================

# Các loại regex nhận diện tiêu đề ở ĐẦU DÒNG (Heading thật)
# Hỗ trợ cả trường hợp có hoặc không có ký hiệu Markdown '#' đứng đầu
PATTERNS = {
    "PHAN": re.compile(
        r"^\s*(?:#+\s*)?(?:PHẦN|Phần)\s+([A-Z\d]+|[a-z\d]+)\b.*$", re.MULTILINE | re.IGNORECASE
    ),
    "CHUONG": re.compile(
        r"^\s*(?:#+\s*)?(?:CHƯƠNG|Chương)\s+([IVXLCDM\d]+)\b.*$", re.MULTILINE | re.IGNORECASE
    ),
    "MUC": re.compile(
        r"^\s*(?:#+\s*)?(?:MỤC|Mục)\s+([IVXLCDM\d]+|[A-Z\d]+)\b.*$", re.MULTILINE | re.IGNORECASE
    ),
    "DIEU": re.compile(r"^\s*(?:#+\s*)?(?:ĐIỀU|Điều)\s+(\d+)\b.*$", re.MULTILINE | re.IGNORECASE),
    # Định dạng các khoản đánh số đơn lẻ đầu dòng: e.g. "1. ", "2. "
    "KHOAN": re.compile(r"^\s*(?:#+\s*)?(\d+)\.\s+.*$", re.MULTILINE),
    # Định dạng La Mã đứng đầu dòng: e.g. "## I. Quyền lợi", "I. Quyền lợi"
    "ROMAN": re.compile(r"^\s*(?:#+\s*)?([IVXLCDM]+)\.\s+.*$", re.MULTILINE),
    # Định dạng số Decimal phân cấp: e.g. "## 1.1. ", "1.2.1. "
    "DECIMAL": re.compile(r"^\s*(?:#+\s*)?(\d+(?:\.\d+)+)\.?\s+.*$", re.MULTILINE),
}


# ==============================================================================
# PHẦN 2: Thử nghiệm phân biệt Heading thật vs Cross-reference trên Bảo Việt
# ==============================================================================


def test_heading_vs_crossref(text: str):
    """Đếm heading thật vs cross-reference trên văn bản Bảo Việt."""
    results.append("=" * 80)
    results.append("THÍ NGHIỆM 2: PHÂN BIỆT HEADING THẬT VS CROSS-REFERENCE TRÊN BẢO VIỆT")
    results.append("=" * 80)

    # 1. Heading thật (ở đầu dòng):
    headings = re.findall(PATTERNS["DIEU"], text)

    # 2. Toàn bộ chữ "Điều" trong văn bản (cả đầu dòng và giữa câu):
    # Dùng lookbehind để loại bỏ đầu dòng nếu muốn đếm cross-ref riêng,
    # hoặc đếm tổng rồi trừ đi.
    all_mentions = re.findall(r"\b(?:ĐIỀU|Điều)\s+\d+\b", text)

    headings_count = len(headings)
    total_mentions = len(all_mentions)
    cross_refs_count = total_mentions - headings_count

    results.append(f"Tổng số lần từ khóa 'Điều' xuất hiện: {total_mentions}")
    results.append(f"Số lượng Heading 'Điều' thật (ở đầu dòng): {headings_count}")
    results.append(f"Số lượng Tham chiếu chéo (Cross-reference): {cross_refs_count}")

    # In ra một số dòng chứa cross-reference
    results.append("\n--- Các dòng chứa Tham chiếu chéo (mẫu): ---")
    lines = text.split("\n")
    sample_count = 0
    for line in lines:
        line_strip = line.strip()
        # Nếu dòng chứa "Điều" nhưng không bắt đầu bằng "Điều"
        if re.search(r"\b(?:ĐIỀU|Điều)\s+\d+\b", line_strip) and not re.match(
            r"^(?:ĐIỀU|Điều)\s+\d+", line_strip
        ):
            results.append(f"  [Cross-ref line]: {line_strip}")
            sample_count += 1
            if sample_count >= 5:
                break

    # Tính False Positive Rate nếu dùng regex tìm kiếm thông thường (không có ^) để làm heading
    # False Positive ở đây là nhận diện nhầm các tham chiếu chéo thành tiêu đề mới.
    if total_mentions > 0:
        fpr = (cross_refs_count / total_mentions) * 100
        results.append(f"\nTỷ lệ False Positive nếu không dùng anchor '^': {fpr:.2f}%")


# ==============================================================================
# PHẦN 3: Thuật toán Frequency-based Hierarchy Inference
# ==============================================================================


def infer_hierarchy(text: str, file_label: str):
    """Suy luận phân cấp dựa trên tần suất của từng loại pattern tiêu đề."""
    results.append("\n" + "=" * 80)
    results.append(f"THÍ NGHIỆM 3: SUY LUẬN PHÂN CẤP (FREQUENCY-BASED HIERARCHY) - {file_label}")
    results.append("=" * 80)

    counts = {}
    for pat_name, pat in PATTERNS.items():
        matches = pat.findall(text)
        if len(matches) > 0:
            counts[pat_name] = len(matches)

    # Sắp xếp các pattern có xuất hiện theo tần suất tăng dần (Cấp cao nhất xuất hiện ít nhất)
    inferred = sorted(counts.items(), key=lambda x: x[1])

    results.append("Tần suất xuất hiện các pattern:")
    for pat_name, count in counts.items():
        results.append(f"  - {pat_name}: {count} lần")

    results.append("\nCấu trúc phân cấp suy luận (từ cao đến thấp):")
    hierarchy_str = " -> ".join([pat_name for pat_name, _ in inferred])
    results.append(f"  {hierarchy_str}")


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 80)
    print("NOTEBOOK 04: REGEX HEADING DETECTION & PROFILING")
    print("=" * 80)

    # 1. Trích xuất tài liệu cần thiết
    aia_text = run_quick_extraction(AIA_PDF, "mineru_aia_pages", 0, 6)
    baoviet_text = run_quick_extraction(BAOVIET_PDF, "mineru_baoviet_pages", 0, 4)

    daiichi_text = ""
    if DAIICHI_MD.exists():
        daiichi_text = DAIICHI_MD.read_text(encoding="utf-8")

    law_text = ""
    if LAW_MD.exists():
        law_text = LAW_MD.read_text(encoding="utf-8")

    # --- Thí nghiệm 1: Kiểm thử các Regex Patterns trên AIA ---
    results.append("=" * 80)
    results.append("THÍ NGHIỆM 1: KIỂM THỬ REGEX TRÊN AIA (Có Số La Mã)")
    results.append("=" * 80)
    if aia_text:
        # AIA thường dùng chữ số La Mã làm Chương/Mục
        roman_headings = PATTERNS["ROMAN"].findall(aia_text)
        results.append(f"Số lượng tiêu đề số La Mã (ROMAN) phát hiện: {len(roman_headings)}")
        results.append(f"Mẫu tiêu đề số La Mã: {roman_headings[:5]}")
    else:
        results.append("❌ Bỏ qua thí nghiệm AIA vì lỗi trích xuất.")

    # --- Thí nghiệm 2: Đếm heading thật vs cross-reference trên Bảo Việt ---
    if baoviet_text:
        test_heading_vs_crossref(baoviet_text)
    else:
        results.append("❌ Bỏ qua thí nghiệm Bảo Việt vì lỗi trích xuất.")

    # --- Thí nghiệm 3: Thử nghiệm suy luận phân cấp tự động trên Luật ---
    if law_text:
        infer_hierarchy(law_text, "LUẬT KINH DOANH BẢO HIỂM")
    else:
        results.append("❌ Bỏ qua thí nghiệm Luật vì không tìm thấy file MD trích xuất trước đó.")

    # --- Thí nghiệm 4: Thử nghiệm suy luận phân cấp tự động trên Dai-ichi ---
    if daiichi_text:
        infer_hierarchy(daiichi_text, "DAI-ICHI LIFE")

    # Ghi kết quả
    output_file = OUTPUT_DIR / "heading_detection_results.txt"
    output_file.write_text("\n".join(results), encoding="utf-8")
    print(f"\nDone! Results saved to: {output_file}")


if __name__ == "__main__":
    main()
