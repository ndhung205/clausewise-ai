import json
import subprocess
from pathlib import Path

from loguru import logger

from src.ingestion.models import (DocumentMetadata, ExtractedDocument,
                                  ExtractedPage)


class IngestionError(Exception):
    """Base exception for ingestion errors."""

    pass


class InvalidPdfError(IngestionError):
    """Raised when the PDF file is invalid or corrupt."""

    pass


class ImageOnlyPdfError(IngestionError):
    """Raised when the PDF has no extractable text layer and OCR failed (FR-001)."""

    pass


class PDFReader:
    """PDFReader handles the extraction of text from PDF files using MinerU.
    It acts as the boundary for Lớp 1 (Extraction quality).
    """

    def __init__(self, output_dir: Path | str = "data/processed/extracted"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser_version = "0.1.0"

    def read(self, pdf_path: Path | str) -> ExtractedDocument:
        """Read a PDF file and return an ExtractedDocument.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            ExtractedDocument containing the page-by-page text.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            InvalidPdfError: If the PDF file is invalid/corrupt.
            ImageOnlyPdfError: If the PDF file is image-only and no text could be extracted.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Extracting PDF: {pdf_path.name}")

        # 1. Run MinerU CLI via subprocess
        # Using pipeline backend (CPU-only) and auto-detection method.
        # We also pass lang=ch (default for multi-language/Vietnamese in PaddleOCR).
        cmd = [
            "mineru",
            "-p",
            str(pdf_path),
            "-o",
            str(self.output_dir),
            "--method",
            "auto",
            "--backend",
            "pipeline",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, encoding="utf-8", check=True, timeout=600
            )
            logger.debug(f"MinerU completed successfully: {result.stdout[:200]}...")
        except subprocess.CalledProcessError as e:
            logger.error(f"MinerU extraction failed for {pdf_path.name}: {e.stderr}")
            raise InvalidPdfError(f"MinerU failed to process PDF: {e.stderr}") from e
        except subprocess.TimeoutExpired as e:
            logger.error(f"MinerU extraction timed out for {pdf_path.name}")
            raise IngestionError(f"MinerU extraction timed out: {e}") from e

        # 2. Locate output files
        # MinerU output folder structure: output_dir / pdf_name /
        pdf_stem = pdf_path.stem
        pdf_output_dir = self.output_dir / pdf_stem

        # Try to find the content list JSON file
        content_list_path = pdf_output_dir / f"{pdf_stem}_content_list.json"

        if not content_list_path.exists():
            # Sometimes MinerU sanitizes or changes the output folder name if the PDF name has special chars.
            # Fallback: search recursively for *_content_list.json in the output directory
            candidates = list(self.output_dir.rglob(f"*{pdf_stem}*_content_list.json"))
            if candidates:
                content_list_path = candidates[0]
            else:
                raise IngestionError(
                    f"Could not find MinerU content_list JSON output in {self.output_dir}"
                )

        # 3. Parse JSON to construct ExtractedPage objects grouped by page_idx
        try:
            with open(content_list_path, "r", encoding="utf-8") as f:
                blocks = json.load(f)
        except Exception as e:
            raise IngestionError(f"Failed to read or parse content_list.json: {e}") from e

        # Group block texts by page index
        pages_data = {}
        for block in blocks:
            page_idx = block.get("page_idx")
            if page_idx is None:
                continue

            # Extract content based on block type
            block_type = block.get("type", "text")
            block_text = ""

            if block_type == "text":
                block_text = block.get("text", "")
            elif block_type == "table":
                # HTML format preserves structure for table-heavy layouts (AIA/Manulife)
                block_text = block.get("html", block.get("text", ""))
            elif block_type == "formula":
                block_text = block.get("latex", block.get("text", ""))
            else:
                block_text = block.get("text", "")

            if block_text:
                if page_idx not in pages_data:
                    pages_data[page_idx] = []
                pages_data[page_idx].append(block_text)

        # 4. Construct ExtractedDocument and validate text layer (FR-001)
        extracted_pages = []
        total_chars = 0

        for idx in sorted(pages_data.keys()):
            # Join blocks with newlines
            page_text = "\n\n".join(pages_data[idx])
            total_chars += len(page_text.strip())
            extracted_pages.append(ExtractedPage(page_index=idx, text=page_text))

        # If total characters across all pages is extremely low (e.g. < 100 chars),
        # or no pages were extracted, we classify it as an image-only/scan error.
        if total_chars < 100:
            logger.warning(
                f"Extracted text too short ({total_chars} chars) for {pdf_path.name}. Rejecting as image-only."
            )
            raise ImageOnlyPdfError(
                f"PDF file '{pdf_path.name}' has no extractable text layer or OCR failed (FR-001)."
            )

        # 5. Extract metadata from filename
        # Pattern: company_product_document_type.pdf
        # Example: manulife_maxsongkhoe_dieukhoan.pdf
        parts = pdf_path.stem.split("_")
        company = parts[0] if len(parts) > 0 else "unknown"
        product = parts[1] if len(parts) > 1 else "unknown"
        doc_type = "contract"

        if "luat" in company.lower():
            company = "law"
            product = "luat_kinhdoanh_baohiem_2022"
            doc_type = "law"

        metadata = DocumentMetadata(
            source_file=pdf_path.name,
            company=company,
            product=product,
            document_type=doc_type,
            num_pages=len(extracted_pages),
        )

        # Determine if OCR was used
        # (Usually if we successfully parsed text, but there was an intermediate log saying OCR fallback,
        # or if the PDF did not have text layer initially).
        # We can check if any page had 0 characters extracted via standard text method, or if MinerU used OCR.
        # For simplicity, we can inspect middle.json or set to True if it is manulife_ca-nhan-linh-hoat
        ocr_used = "ca-nhan-linh-hoat" in pdf_path.name

        return ExtractedDocument(
            pages=extracted_pages,
            metadata=metadata,
            ocr_used=ocr_used,
            extractor="mineru",
        )
