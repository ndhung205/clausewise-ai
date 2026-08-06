from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata of the document extracted from the PDF file or filename."""

    source_file: str = Field(..., description="Tên file PDF gốc")
    company: str = Field(..., description="Tên công ty bảo hiểm (hoặc 'law' cho văn bản luật)")
    product: str = Field(..., description="Tên sản phẩm bảo hiểm (hoặc tên bộ luật)")
    document_type: str = Field(..., description="Loại tài liệu: 'contract' hoặc 'law'")
    num_pages: int = Field(..., description="Tổng số trang của tài liệu")


class ExtractedPage(BaseModel):
    """Represent one extracted page from the PDF document."""

    page_index: int = Field(..., description="Trang thứ mấy, bắt đầu từ 0")
    text: str = Field(..., description="Nội dung văn bản thô của trang")


class ExtractedDocument(BaseModel):
    """Format-agnostic intermediate representation of the extracted document.
    This serves as the boundary between PDF extraction (Layer 1) and downstream
    parsing/profiling/chunking (Layer 2).
    """

    pages: list[ExtractedPage] = Field(..., description="Danh sách các trang đã trích xuất")
    metadata: DocumentMetadata = Field(..., description="Metadata của tài liệu")
    ocr_used: bool = Field(False, description="Đã có dùng OCR để trích xuất hay không")
    extractor: str = Field("mineru", description="Tên công cụ dùng để trích xuất (ví dụ: 'mineru')")

    def get_full_text(self) -> str:
        """Helper to get the concatenated text of all pages with page markers."""
        return "\n\n".join([page.text for page in self.pages])


class HeadingMatch(BaseModel):
    """Represent a heading found in the document text."""

    pattern_type: str = Field(
        ..., description="Loại heading: CHUONG, MUC, DIEU, KHOAN, DIEM, ROMAN, DECIMAL"
    )
    match_text: str = Field(..., description="Toàn bộ text của heading (ví dụ: 'Điều 5. Loại trừ')")
    start_idx: int = Field(..., description="Index bắt đầu trong full text")
    end_idx: int = Field(..., description="Index kết thúc trong full text")
    page_index: int = Field(..., description="Trang chứa heading này")


class DocumentProfile(BaseModel):
    """Represent the structural profile inferred from the document heading patterns."""

    profile_type: str = Field(
        ..., description="Loại cấu trúc (ví dụ: 'chapter_article_continuous')"
    )
    levels: list[str] = Field(..., description="Thứ tự phân cấp của các heading từ cao xuống thấp")
    confidence: float = Field(..., description="Độ tin cậy của việc nhận diện cấu trúc (0.0 - 1.0)")
    pattern_counts: dict[str, int] = Field(..., description="Số lần xuất hiện của mỗi loại pattern")


class Chunk(BaseModel):
    """Represent the final structural chunk to be stored in the vector database."""

    text: str = Field(..., description="Nội dung điều khoản của chunk")

    # 13 metadata fields required by dataset.md
    source_file: str = Field(..., description="Tên file gốc")
    company: str = Field(..., description="Tên công ty")
    product: str = Field(..., description="Tên sản phẩm")
    document_type: str = Field(..., description="Loại tài liệu: contract / law")
    page_start: int = Field(..., description="Trang bắt đầu")
    page_end: int = Field(..., description="Trang kết thúc")
    hierarchy_path: str = Field(
        ..., description="Đường dẫn phân cấp đầy đủ (ví dụ: 'CHƯƠNG I / Điều 3 / 3.1')"
    )
    section: str = Field(..., description="Heading gần nhất")
    extractor: str = Field(..., description="Tool extraction Lớp 1 (mineru)")
    profile_type: str = Field(..., description="Profile structure đã nhận diện")
    hierarchy_confidence: float = Field(..., description="Độ tin cậy profiling")
    ocr_used: bool = Field(..., description="Có dùng OCR không")
    parser_version: str = Field(..., description="Phiên bản parser")
