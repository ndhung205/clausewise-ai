"""
Notebook Experiment 02: Text Cleaning Exploration
==================================================
Mục tiêu:
  1. Chạy MinerU trích xuất trang 0-3 của Prudential 'pru-bao-ve-toi-da2' và tìm lỗi khoảng trắng (spacing).
  2. Áp dụng các quy tắc clean trong text_cleaner.py và đánh giá.
  3. Mô phỏng và khắc phục lỗi ngắt dòng tiêu đề (heading wrap) bằng logic tiền xử lý.

Chạy:
  $env:PYTHONPATH="d:\HocTap\Project_NLP_RAG\clausewise-ai"; $env:PYTHONIOENCODING="utf-8"; python notebooks/02_text_cleaning_exploration.py
"""

import re
import subprocess
from pathlib import Path

from src.ingestion.text_cleaner import clean_text_content

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw" / "contracts"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "extraction_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PRUDENTIAL_PDF = DATA_DIR / "prudential_pru-bao-ve-toi-da2-tnc_dieukhoan.pdf"
results = []


# ==============================================================================
# PHẦN 1: Thử nghiệm trích xuất và sửa khoảng trắng Prudential
# ==============================================================================


def run_prudential_extraction() -> str:
    """Trích xuất trang 0-3 của Prudential bằng MinerU và trả về văn bản Markdown."""
    print("1. Đang chạy MinerU trên trang 0-3 của Prudential PDF...")
    out_dir = OUTPUT_DIR / "mineru_prudential_pages"

    cmd = [
        "mineru",
        "-p",
        str(PRUDENTIAL_PDF),
        "-o",
        str(out_dir),
        "-s",
        "0",
        "-e",
        "3",
        "--method",
        "auto",
        "--backend",
        "pipeline",
    ]

    # Chạy MinerU CLI
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=300)
    if result.returncode != 0:
        print("❌ Lỗi MinerU:", result.stderr[:300])
        return ""

    md_files = list(out_dir.rglob("*.md"))
    if not md_files:
        print("❌ Không tìm thấy markdown output")
        return ""

    return md_files[0].read_text(encoding="utf-8")


# ==============================================================================
# PHẦN 2: Thử nghiệm sửa Heading Wrap (Mô phỏng & Proof of Concept)
# ==============================================================================


def fix_heading_wrap(text: str) -> tuple[str, int]:
    """Logic tìm và nối các heading bị ngắt dòng (wrap) vật lý."""
    lines = text.split("\n")
    fixed_lines = []
    i = 0
    merge_count = 0

    # Định nghĩa regex nhận diện heading bị xuống dòng vật lý
    # Ví dụ: dòng bắt đầu bằng '## ĐIỀU \d+' hoặc '## \d+.\d+'
    heading_pattern = re.compile(r"^##\s+([Đđ]IỀU\s+\d+|[A-Z\d]+\.\d+)", re.IGNORECASE)

    while i < len(lines):
        line = lines[i].strip()

        # Nếu là dòng cuối, không thể nối tiếp
        if i == len(lines) - 1:
            fixed_lines.append(lines[i])
            i += 1
            continue

        next_line = lines[i + 1].strip()

        # Kiểm tra xem dòng hiện tại có phải heading không
        if heading_pattern.match(line) and next_line:
            # Điều kiện nối: dòng sau không bắt đầu bằng dấu # và không bắt đầu bằng số/mục mới
            # và bắt đầu bằng chữ thường hoặc từ nối tiếp ý
            is_next_lowercase = next_line[0].islower() if next_line else False
            is_next_not_header = not next_line.startswith("#") and not re.match(
                r"^(\d+\.|\-|[a-z]\))", next_line
            )

            if is_next_lowercase or (is_next_not_header and len(next_line) < 100):
                # Nối hai dòng với khoảng trắng
                merged_line = line + " " + next_line
                fixed_lines.append(merged_line)
                results.append(f"   [Nối heading]: '{line}' + '{next_line}' -> '{merged_line}'")
                merge_count += 1
                i += 2  # Bỏ qua dòng tiếp theo vì đã gộp
                continue

        fixed_lines.append(lines[i])
        i += 1

    return "\n".join(fixed_lines), merge_count


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 80)
    print("NOTEBOOK 02: TEXT CLEANING EXPLORATION")
    print("=" * 80)

    # --- Thí nghiệm 1: Prudential spacing ---
    results.append("=" * 80)
    results.append("THÍ NGHIỆM 1: SỬA SPACING TRONG PRUDENTIAL")
    results.append("=" * 80)

    md_content_pru = run_prudential_extraction()
    if md_content_pru:
        # Tìm các lỗi spacing trước khi clean (chỉ khớp các từ có khoảng trắng ở giữa)
        spacing_err_pat = (
            r"\b(?:[Đđ]\s+I\s*[ÊêỀề]\s*U|[Đđ]\s*I\s+[ÊêỀề]\s*U|[Đđ]\s*I\s*[ÊêỀề]\s+U)\b"
        )
        spacing_errors_before = re.findall(spacing_err_pat, md_content_pru, re.IGNORECASE)
        results.append(
            f"Số lỗi spacing thực tế phát hiện trước khi clean: {len(spacing_errors_before)}"
        )
        if spacing_errors_before:
            results.append(f"Mẫu lỗi phát hiện: {list(set(spacing_errors_before))}")

        # Clean text
        cleaned_content_pru = clean_text_content(md_content_pru)

        spacing_errors_after = re.findall(spacing_err_pat, cleaned_content_pru, re.IGNORECASE)
        results.append(f"Số lỗi spacing thực tế sau khi clean: {len(spacing_errors_after)}")

        # Show một đoạn text chứa từ khóa đã được sửa
        results.append("\n--- Xem đoạn văn bản đã được clean sửa lỗi 'ĐI ỀU': ---")
        # Tìm dòng chứa 'ĐIỀU' hoặc 'Điều'
        for line in cleaned_content_pru.split("\n"):
            if "ĐIỀU" in line or "Điều" in line:
                results.append(f"  [Cleaned line]: {line}")
    else:
        results.append("❌ Bỏ qua thí nghiệm Prudential vì lỗi trích xuất.")

    # --- Thí nghiệm 2: Mô phỏng Heading Wrap ---
    results.append("\n" + "=" * 80)
    results.append("THÍ NGHIỆM 2: SỬA HEADING WRAP (MÔ PHỎNG)")
    results.append("=" * 80)

    # Do MinerU phân tích layout rất tốt nên đã tự động nối các heading bị wrap trong Dai-ichi.
    # Ta tạo một đoạn văn bản giả lập chứa heading wrap để kiểm tra logic của bộ tiền xử lý.
    mock_wrapped_text = """
## ĐIỀU 5. Loại trừ bảo hiểm đối với trường hợp tự tử hoặc tự
gây thương tích cho bản thân dù trong trạng thái tỉnh táo hay mất trí.

## 2.3. Nghĩa vụ cung cấp thông tin của Bên mua bảo hiểm và Người
được bảo hiểm để đảm bảo tính trung thực tuyệt đối.
"""
    results.append("--- Văn bản trước khi nối heading wrap: ---")
    results.append(mock_wrapped_text.strip())

    results.append("\n--- Quá trình xử lý: ---")
    fixed_text, wraps_fixed = fix_heading_wrap(mock_wrapped_text)

    results.append(f"\nSố lượng heading bị wrap được sửa: {wraps_fixed}")
    results.append("\n--- Văn bản sau khi nối heading wrap: ---")
    results.append(fixed_text.strip())

    # Ghi file kết quả
    output_file = OUTPUT_DIR / "text_cleaning_results.txt"
    output_file.write_text("\n".join(results), encoding="utf-8")
    print(f"\nDone! Results saved to: {output_file}")


if __name__ == "__main__":
    main()
