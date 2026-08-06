"""
Notebook Experiment 03: Chunking Strategies
===========================================
Mục tiêu:
  1. Trích xuất Điều 4 (Giải thích từ ngữ) từ Luật Kinh doanh Bảo hiểm 2022.
  2. Mô phỏng fixed-size chunking (500 chars, overlap 50) và chỉ ra các vết cắt đứt câu.
  3. Mô phỏng clause-aware chunking (chia theo Khoản/Điểm định nghĩa) và so sánh ngữ nghĩa.

Chạy:
  $env:PYTHONPATH="d:\HocTap\Project_NLP_RAG\clausewise-ai"; $env:PYTHONIOENCODING="utf-8"; python notebooks/03_chunking_strategies.py
"""

import re
import subprocess
from pathlib import Path

from src.ingestion.text_cleaner import clean_text_content

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw" / "laws"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "extraction_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LAW_PDF = DATA_DIR / "luat_kinhdoanh_baohiem_2022_08qh15.pdf"
results = []


# ==============================================================================
# PHẦN 1: Trích xuất Điều 4 bằng MinerU
# ==============================================================================


def run_law_extraction() -> str:
    """Trích xuất trang 1-3 (0-indexed, tức trang 2,3,4 vật lý) của Luật bằng MinerU."""
    print("1. Đang chạy MinerU trên trang 1-3 của Luật...")
    out_dir = OUTPUT_DIR / "mineru_law_pages"

    cmd = [
        "mineru",
        "-p",
        str(LAW_PDF),
        "-o",
        str(out_dir),
        "-s",
        "1",
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

    raw_text = md_files[0].read_text(encoding="utf-8")
    return clean_text_content(raw_text)


# ==============================================================================
# PHẦN 2: Mô phỏng Fixed-size Chunking
# ==============================================================================


def chunk_fixed_size(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Cắt text theo kích thước cố định có overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


# ==============================================================================
# PHẦN 3: Mô phỏng Clause-aware Chunking
# ==============================================================================


def chunk_clause_aware(text: str) -> list[str]:
    """Cắt text theo từng định nghĩa (ví dụ: '1. ', '2. ', ..., '23. ')."""
    # Regex tìm các định nghĩa bắt đầu bằng số dạng '1. ', '2. ', ... ở đầu dòng
    # hoặc sau dấu xuống dòng.
    # Ta split bằng regex này nhưng giữ lại delimiter.
    pattern = r"(\n\d+\.\s+)"
    parts = re.split(pattern, text)

    chunks = []
    # Phần đầu tiên trước định nghĩa số 1 (tiêu đề Điều 4)
    if parts[0].strip():
        chunks.append(parts[0].strip())

    # Ghép delimiter với nội dung tương ứng
    i = 1
    while i < len(parts):
        delimiter = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        chunks.append((delimiter + content).strip())
        i += 2

    return chunks


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 80)
    print("NOTEBOOK 03: CHUNKING STRATEGIES COMPARISON")
    print("=" * 80)

    text = run_law_extraction()
    if not text:
        print("❌ Lỗi trích xuất văn bản.")
        return

    # Trích xuất nội dung Điều 4 để làm thí nghiệm rõ ràng
    # Điều 4 bắt đầu bằng 'Điều 4. Giải thích từ ngữ' và kết thúc khi sang 'Điều 5'
    start_match = re.search(r"Điều 4\.\s+Giải thích từ ngữ", text, re.IGNORECASE)
    end_match = re.search(r"Điều 5\.\s+", text, re.IGNORECASE)

    if start_match:
        start_idx = start_match.start()
        end_idx = end_match.start() if end_match else len(text)
        dieu_4_text = text[start_idx:end_idx].strip()
    else:
        print("⚠️ Không định vị được Điều 4 bằng regex, lấy toàn bộ text trích xuất.")
        dieu_4_text = text.strip()

    results.append("=" * 80)
    results.append("THÍ NGHIỆM 1: FIXED-SIZE CHUNKING (Size=500, Overlap=50)")
    results.append("=" * 80)

    fixed_chunks = chunk_fixed_size(dieu_4_text, size=500, overlap=50)
    results.append(f"Tổng số chunk tạo ra: {len(fixed_chunks)}\n")

    # In ra 3 chunk đầu tiên và chỉ ra vị trí bị cắt đứt ngữ nghĩa
    for idx, chunk in enumerate(fixed_chunks[:3]):
        results.append(f"--- CHUNK {idx+1} (Độ dài: {len(chunk)} ký tự) ---")
        results.append(chunk)
        # Chỉ ra vết cắt ở cuối chunk
        last_chars = chunk[-60:].strip()
        results.append(f"⚠️ Vết cắt cuối chunk: '... {last_chars}'")
        results.append("-" * 40)

    results.append("\n" + "=" * 80)
    results.append("THÍ NGHIỆM 2: CLAUSE-AWARE CHUNKING (Theo Khoản định nghĩa)")
    results.append("=" * 80)

    clause_chunks = chunk_clause_aware(dieu_4_text)
    results.append(f"Tổng số chunk tạo ra: {len(clause_chunks)}\n")

    # In ra 4 chunk định nghĩa đầu tiên
    for idx, chunk in enumerate(clause_chunks[1:5]):  # Bỏ qua chunk 0 là tiêu đề điều
        results.append(f"--- CHUNK ĐỊNH NGHĨA {idx+1} (Độ dài: {len(chunk)} ký tự) ---")
        results.append(chunk)
        results.append("-" * 40)

    # Ghi kết quả so sánh
    output_file = OUTPUT_DIR / "chunking_results.txt"
    output_file.write_text("\n".join(results), encoding="utf-8")
    print(f"\nDone! Results saved to: {output_file}")


if __name__ == "__main__":
    main()
