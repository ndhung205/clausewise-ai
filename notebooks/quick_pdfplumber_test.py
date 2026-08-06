"""Quick test: pdfplumber trên 3 file test cases."""

from pathlib import Path

import pdfplumber

DATA_DIR = Path(r"d:\HocTap\Project_NLP_RAG\clausewise-ai\data\raw\contracts")
OUTPUT = Path(r"d:\HocTap\Project_NLP_RAG\clausewise-ai\data\processed\extraction_comparison")
OUTPUT.mkdir(parents=True, exist_ok=True)

files = {
    "two_column": DATA_DIR / "manulife_maxsongkhoe_dieukhoan.pdf",
    "image_only": DATA_DIR / "manulife_ca-nhan-linh-hoat-khong-chia-lai_dieukhoan.pdf",
    "single_column": DATA_DIR / "daiichilife_anphatdaututhinhvuong_dieukhoan.pdf",
}

results = []

for label, pdf_path in files.items():
    results.append(f"\n{'='*80}")
    results.append(f"📄 {label}: {pdf_path.name}")
    results.append(f"{'='*80}")

    with pdfplumber.open(pdf_path) as pdf:
        results.append(f"Tổng số trang: {len(pdf.pages)}")
        total_chars = 0
        for i in range(min(3, len(pdf.pages))):
            text = pdf.pages[i].extract_text() or ""
            total_chars += len(text)
            results.append(f"\n--- Trang {i+1} ({len(text)} ký tự) ---")
            results.append(text[:800] if text else "(trống — 0 ký tự)")
            results.append("...")

        results.append(f"\n→ Tổng ký tự (3 trang đầu): {total_chars:,}")
        if total_chars == 0:
            results.append("⚠️  File image-only — pdfplumber không extract được text!")

output_text = "\n".join(results)
out_file = OUTPUT / "pdfplumber_results.txt"
out_file.write_text(output_text, encoding="utf-8")
print(f"Done! Results saved to: {out_file}")
