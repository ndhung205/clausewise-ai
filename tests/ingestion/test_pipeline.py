import pytest

from src.ingestion.chunker import AdaptiveChunker
from src.ingestion.models import (DocumentMetadata, ExtractedDocument,
                                  ExtractedPage)
from src.ingestion.structure_profiler import (DocumentStructureProfiler,
                                              StructureProfileError)
from src.ingestion.text_cleaner import clean_document, clean_text_content


def test_clean_text_content_basic():
    """Test standard spacing corrections and unicode normalization."""
    # Test spacing in 'ĐI ỀU' with tone marks
    assert clean_text_content("ĐI ỀU 1. QUY ĐỊNH") == "ĐIỀU 1. QUY ĐỊNH"
    assert clean_text_content("Đi ều 2. Điều khoản") == "Điều 2. Điều khoản"

    # Test spacing in other structural words
    assert clean_text_content("M Ụ C L Ụ C") == "MỤC LỤC"
    assert clean_text_content("K H O Ả N 1") == "KHOẢN 1"

    # Test collapse spaces
    assert clean_text_content("Điều  1.   Nội   dung") == "Điều 1. Nội dung"

    # Test space before punctuation
    assert clean_text_content("Quyền lợi , nghĩa vụ .") == "Quyền lợi, nghĩa vụ."


def test_clean_text_content_html_flatten():
    """Test flattening of HTML table cell headings used in AIA PDFs."""
    html_text = '<tr><td colspan="2">IV. Những điều khoản chung</td></tr>'
    assert clean_text_content(html_text) == "## IV. Những điều khoản chung"

    # Ensure long text in cell is NOT matched as heading (length limit check)
    long_html = '<tr><td colspan="2">I. Đây là một câu mô tả rất dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài dài tại Điều 8.</td></tr>'
    assert clean_text_content(long_html) == long_html


def test_clean_text_content_newline_merge():
    """Test merging of titles written on the line below the identifier."""
    # Chapter title merge
    assert clean_text_content("Chương II\nHỢP ĐỒNG BẢO HIỂM") == "Chương II. HỢP ĐỒNG BẢO HIỂM"

    # Section title merge
    assert (
        clean_text_content("Mục 1\nQUY ĐỊNH CHUNG VỀ HỢP ĐỒNG BẢO HIỂM")
        == "Mục 1. QUY ĐỊNH CHUNG VỀ HỢP ĐỒNG BẢO HIỂM"
    )

    # Article title merge
    assert clean_text_content("Điều 15\nHợp đồng bảo hiểm") == "Điều 15. Hợp đồng bảo hiểm"

    # Ensure it does NOT merge if the next line starts with a number (indicating a clause, not a title)
    assert (
        clean_text_content("Điều 1\n1. Luật này áp dụng cho...")
        == "Điều 1\n1. Luật này áp dụng cho..."
    )


def test_profiler_and_chunker_basic():
    """Test structure profiling and adaptive chunking on mock document text."""
    # Create mock pages with sequential headings
    pages = [
        ExtractedPage(
            page_index=0,
            text="## PHẦN I: NHỮNG ĐIỀU KHOẢN CHUNG\nĐiều 1. Định nghĩa\nNội dung điều 1 ở đây.",
        ),
        ExtractedPage(
            page_index=1,
            text="## Điều 2. Quyền lợi\n2.1. Quyền lợi chính: chi trả tiền.\n2.2. Quyền lợi phụ: hỗ trợ khác.",
        ),
        ExtractedPage(
            page_index=2,
            text="## Điều 3. Điều khoản loại trừ\nCác trường hợp không chi trả được nêu cụ thể.",
        ),
    ]

    metadata = DocumentMetadata(
        source_file="mock_contract.pdf",
        company="Dai-ichi",
        product="An Phat",
        document_type="contract",
        num_pages=3,
    )

    doc = ExtractedDocument(pages=pages, metadata=metadata)
    cleaned_doc = clean_document(doc)

    # 1. Profile Document
    profiler = DocumentStructureProfiler(min_confidence=0.5)
    profile, headings = profiler.profile_document(cleaned_doc)

    assert len(headings) == 6  # PHẦN I, Điều 1, Điều 2, 2.1, 2.2, Điều 3
    assert profile.profile_type == "part_article"  # PHAN and DIEU are present
    assert profile.confidence >= 0.8  # Sequential 1, 2, 3 -> high confidence

    # 2. Chunk Document
    chunker = AdaptiveChunker(max_chunk_size=500)
    chunks = chunker.chunk_document(cleaned_doc, profile, headings)

    assert len(chunks) == 6

    # Verify metadata fields on first chunk
    c1 = chunks[0]
    assert c1.section == "## PHẦN I: NHỮNG ĐIỀU KHOẢN CHUNG"
    assert "PHẦN I" in c1.hierarchy_path
    assert c1.company == "Dai-ichi"
    assert c1.page_start == 0
    assert c1.page_end == 0

    # Verify metadata fields on decimal chunk
    c4 = chunks[3]  # should be 2.1
    assert c4.section == "2.1. Quyền lợi chính: chi trả tiền."
    assert "Điều 2" in c4.hierarchy_path
    assert "PHẦN I" in c4.hierarchy_path
    assert c4.page_start == 1


def test_profiler_reject_low_confidence():
    """Test that the profiler rejects documents with chaotic or non-existent outlines."""
    pages = [
        ExtractedPage(
            page_index=0,
            text="Điều 1. Đầu dòng\nNội dung ở đây.\nĐiều 99. Nhảy số\nMột nội dung khác.\nĐiều 4. Nhảy số tiếp",
        )
    ]

    metadata = DocumentMetadata(
        source_file="bad_contract.pdf",
        company="Manulife",
        product="Linh Hoat",
        document_type="contract",
        num_pages=1,
    )

    doc = ExtractedDocument(pages=pages, metadata=metadata)

    profiler = DocumentStructureProfiler(min_confidence=0.6)

    # Should raise StructureProfileError because of chaotic sequence: 1 -> 99 -> 4 (seq score low)
    with pytest.raises(StructureProfileError):
        profiler.profile_document(doc)
