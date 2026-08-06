"""
Notebook Experiment 01: PDF Extraction Comparison
==================================================
Mục tiêu: So sánh pdfplumber vs MinerU trên dataset ClauseWise.

Thí nghiệm:
  1. pdfplumber extract file Manulife 2 cột → quan sát text bị trộn
  2. MinerU extract cùng file → so sánh reading order
  3. Thử file image-only → quan sát OCR output
  4. Extract thêm 1 file single-column (Dai-ichi) để có baseline

Sau khi chạy xong, ghi kết quả vào docs/journal.md.

Cài đặt trước khi chạy:
  pip install pdfplumber
  pip install -U "mineru[all]"

Lưu ý MinerU:
  - Lần đầu chạy sẽ tự tải model (~2-5 GB) → cần internet + kiên nhẫn
  - Cần tối thiểu 16 GB RAM (theo docs MinerU)
  - Dùng pipeline backend (CPU-only) vì máy không có NVIDIA GPU
"""

from pathlib import Path

# ==============================================================================
# Config
# ==============================================================================

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# 3 file test đại diện cho 3 case khác nhau
FILES = {
    "two_column": DATA_DIR / "contracts" / "manulife_maxsongkhoe_dieukhoan.pdf",
    "image_only": DATA_DIR
    / "contracts"
    / "manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf",
    "single_column": DATA_DIR / "contracts" / "daiichilife_anphatdaututhinhvuong_dieukhoan.pdf",
}

# Số trang extract để so sánh (không cần toàn bộ file)
PAGES_TO_EXTRACT = 3

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed" / "extraction_comparison"


# ==============================================================================
# Phần A: pdfplumber — extraction tuyến tính
# ==============================================================================
# pdfplumber đọc text theo toạ độ (y rồi x), không có layout analysis.
# Với file single-column: hoạt động tốt.
# Với file 2 cột: text bị trộn cột trái + cột phải.
# ==============================================================================


def extract_with_pdfplumber(pdf_path: Path, max_pages: int = PAGES_TO_EXTRACT) -> list[str]:
    """
    Extract text từ PDF bằng pdfplumber (extraction tuyến tính).

    pdfplumber đọc text objects theo toạ độ y (trên → dưới) rồi x (trái → phải).
    Không có layout analysis model → sẽ trộn text nếu PDF có 2 cột.

    Returns:
        list[str]: text mỗi trang (tối đa max_pages trang)
    """
    import pdfplumber

    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[:max_pages]):
            text = page.extract_text() or ""
            pages_text.append(text)
    return pages_text


# ==============================================================================
# Phần B: MinerU — extraction có layout analysis
# ==============================================================================
# MinerU render trang thành ảnh → chạy layout analysis model → reconstruct
# reading order → extract text theo đúng thứ tự đọc.
# Với file 2 cột: đọc hết cột trái trước, rồi mới sang cột phải.
# ==============================================================================


def extract_with_mineru(pdf_path: Path, output_dir: Path) -> list[str]:
    """
    Extract text từ PDF bằng MinerU (pipeline backend, CPU).

    MinerU pipeline:
      render → layout analysis → reading order reconstruction → text extraction
    Nếu trang image-only → tự động chạy PaddleOCR.

    Returns:
        list[str]: text mỗi trang (toàn bộ file)
    """
    import subprocess

    output_dir.mkdir(parents=True, exist_ok=True)

    # Dùng CLI MinerU — đơn giản nhất cho thí nghiệm
    # --method auto: tự detect text-layer hay image-only
    # --backend pipeline: dùng CPU (không cần GPU)
    cmd = [
        "mineru",
        "-p",
        str(pdf_path),
        "-o",
        str(output_dir),
        "--method",
        "auto",
        "--backend",
        "pipeline",
    ]

    print(f"  Đang chạy MinerU trên {pdf_path.name}...")
    print(f"  Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=600)

    if result.returncode != 0:
        print(f"  ❌ MinerU lỗi: {result.stderr[:500]}")
        return []

    # MinerU output: thư mục chứa file .md (Markdown)
    # Tìm file markdown output
    md_files = list(output_dir.rglob("*.md"))
    if not md_files:
        print("  ❌ Không tìm thấy file Markdown output")
        return []

    # Đọc file markdown đầu tiên
    md_content = md_files[0].read_text(encoding="utf-8")

    # MinerU không chia theo trang trong Markdown output
    # → trả về toàn bộ content như 1 phần tử
    return [md_content]


# ==============================================================================
# Phần C: So sánh & In kết quả
# ==============================================================================


def print_comparison(
    label: str, pdf_path: Path, pdfplumber_pages: list[str], mineru_pages: list[str]
) -> None:
    """In so sánh kết quả extraction giữa 2 tool."""

    print(f"\n{'='*80}")
    print(f"📄 {label}: {pdf_path.name}")
    print(f"{'='*80}")

    # pdfplumber
    print("\n--- pdfplumber (extraction tuyến tính) ---")
    if not pdfplumber_pages or all(len(p.strip()) == 0 for p in pdfplumber_pages):
        print("  ⚠️  Không extract được text (0 ký tự)")
        print("  → File có thể là image-only PDF (không có text layer)")
    else:
        total_chars = sum(len(p) for p in pdfplumber_pages)
        print(f"  Số trang extract: {len(pdfplumber_pages)}")
        print(f"  Tổng ký tự: {total_chars:,}")
        print("\n  --- Trang 1 (500 ký tự đầu) ---")
        print(f"  {pdfplumber_pages[0][:500]}")
        if len(pdfplumber_pages) > 1:
            print("\n  --- Trang 2 (500 ký tự đầu) ---")
            print(f"  {pdfplumber_pages[1][:500]}")

    # MinerU
    print("\n--- MinerU (layout analysis + reading order) ---")
    if not mineru_pages or all(len(p.strip()) == 0 for p in mineru_pages):
        print("  ⚠️  Không extract được text")
    else:
        total_chars = sum(len(p) for p in mineru_pages)
        print(f"  Tổng ký tự: {total_chars:,}")
        print("\n  --- Output (1000 ký tự đầu) ---")
        print(f"  {mineru_pages[0][:1000]}")

    print()


def print_observation_prompts() -> None:
    """In các câu hỏi quan sát để ghi vào journal."""

    print(f"\n{'='*80}")
    print("📝 CÂU HỎI QUAN SÁT — ghi kết quả vào docs/journal.md")
    print(f"{'='*80}")
    print(
        """
1. FILE 2 CỘT (Manulife maxsongkhoe):
   - pdfplumber: text có bị trộn cột trái + phải không? Chỗ nào thấy rõ nhất?
   - MinerU: text có đúng thứ tự không? Đọc hết cột trái rồi mới sang phải?
   - So sánh: sự khác biệt lớn nhất ở đâu?

2. FILE IMAGE-ONLY (Manulife ca-nhan-linh-hoat):
   - pdfplumber: có extract được text không? Bao nhiêu ký tự?
   - MinerU: OCR có hoạt động không? Chất lượng text ra sao?
   - Có lỗi OCR nào nhìn thấy được không (ký tự sai, dấu tiếng Việt lỗi)?

3. FILE SINGLE-COLUMN (Dai-ichi anphatdaututhinhvuong):
   - pdfplumber và MinerU có cho kết quả giống nhau không?
   - Nếu giống → chứng minh rằng vấn đề nằm ở layout, không phải tool.

4. TỔNG QUÁT:
   - MinerU output dạng Markdown: heading có được đánh dấu (#) không?
   - Bảng (nếu có) được convert thế nào?
   - Header/footer/watermark có bị loại không?
"""
    )


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 80)
    print("NOTEBOOK 01: PDF EXTRACTION COMPARISON")
    print("pdfplumber (tuyến tính) vs MinerU (layout analysis)")
    print("=" * 80)

    # Kiểm tra files tồn tại
    for label, path in FILES.items():
        if not path.exists():
            print(f"❌ File không tồn tại: {path}")
            return
        print(f"✅ {label}: {path.name} ({path.stat().st_size / 1024:.0f} KB)")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Thí nghiệm 1: File 2 cột ---
    print(f"\n{'─'*40}")
    print("Thí nghiệm 1: File 2 cột (Manulife maxsongkhoe)")
    print(f"{'─'*40}")

    plumber_two_col = extract_with_pdfplumber(FILES["two_column"])
    mineru_two_col = extract_with_mineru(FILES["two_column"], OUTPUT_DIR / "mineru_two_column")
    print_comparison("2 CỘT", FILES["two_column"], plumber_two_col, mineru_two_col)

    # --- Thí nghiệm 2: File image-only ---
    print(f"\n{'─'*40}")
    print("Thí nghiệm 2: File image-only (Manulife ca-nhan-linh-hoat)")
    print(f"{'─'*40}")

    plumber_image = extract_with_pdfplumber(FILES["image_only"])
    mineru_image = extract_with_mineru(FILES["image_only"], OUTPUT_DIR / "mineru_image_only")
    print_comparison("IMAGE-ONLY", FILES["image_only"], plumber_image, mineru_image)

    # --- Thí nghiệm 3: File single-column (baseline) ---
    print(f"\n{'─'*40}")
    print("Thí nghiệm 3: File single-column (Dai-ichi — baseline)")
    print(f"{'─'*40}")

    plumber_single = extract_with_pdfplumber(FILES["single_column"])
    mineru_single = extract_with_mineru(FILES["single_column"], OUTPUT_DIR / "mineru_single_column")
    print_comparison("SINGLE-COLUMN", FILES["single_column"], plumber_single, mineru_single)

    # --- Câu hỏi quan sát ---
    print_observation_prompts()

    print(f"\n✅ Output MinerU đã lưu tại: {OUTPUT_DIR}")
    print("📝 Ghi kết quả quan sát vào docs/journal.md")


if __name__ == "__main__":
    main()
