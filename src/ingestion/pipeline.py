from pathlib import Path

from src.ingestion.chunker import AdaptiveChunker
from src.ingestion.models import Chunk
from src.ingestion.pdf_reader import PDFReader
from src.ingestion.structure_profiler import DocumentStructureProfiler
from src.ingestion.text_cleaner import clean_document


class IngestionPipeline:
    """IngestionPipeline orchestrates the entire PDF ingestion flow.
    It combines PDF extraction (Layer 1), text cleaning, structure profiling,
    and adaptive chunking (Layer 2).
    """

    def __init__(
        self, output_dir: str | Path = "data/processed/extracted", min_confidence: float = 0.6
    ):
        self.reader = PDFReader(output_dir=output_dir)
        self.profiler = DocumentStructureProfiler(min_confidence=min_confidence)
        self.chunker = AdaptiveChunker()

    def process_pdf(self, pdf_path: str | Path) -> list[Chunk]:
        """Process a PDF file and return a list of structured chunks with 13 metadata fields.

        Raises:
            FileNotFoundError: If the file does not exist.
            InvalidPdfError: If the PDF is corrupt.
            ImageOnlyPdfError: If the PDF has no text layer and OCR fails.
            StructureProfileError: If the structural hierarchy cannot be inferred confidently.
        """
        # 1. Trích xuất PDF (Lớp 1)
        doc = self.reader.read(pdf_path)

        # 2. Làm sạch văn bản (Lớp 2)
        cleaned_doc = clean_document(doc)

        # 3. Định hình cấu trúc (Lớp 2)
        profile, headings = self.profiler.profile_document(cleaned_doc)

        # 4. Chia chunk tự thích nghi (Lớp 2)
        chunks = self.chunker.chunk_document(cleaned_doc, profile, headings)

        return chunks
