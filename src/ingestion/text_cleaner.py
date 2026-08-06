import re
import unicodedata

from src.ingestion.models import ExtractedDocument, ExtractedPage


def _fix_case(text: str, correct_word: str) -> str:
    """Helper to keep the case of the original matched text."""
    if text.isupper():
        return correct_word.upper()
    if text.islower():
        return correct_word.lower()
    if text and text[0].isupper():
        return correct_word.capitalize()
    return correct_word


def clean_text_content(text: str) -> str:
    """Clean and normalize a single text string."""
    if not text:
        return ""

    # 1. Normalize Unicode to NFC (ensure combining accents are merged correctly)
    # (e.g., 'o' + ' ́ ' -> 'ó')
    text = unicodedata.normalize("NFC", text)

    # Flatten HTML table cell headings that span the row (e.g. in AIA benefit summary/terms)
    # <tr><td colspan="2">IV. Những điều khoản chung</td></tr> -> ## IV. Những điều khoản chung
    # We limit heading length to 100 chars to avoid matching cell descriptions
    text = re.sub(
        r"<tr>\s*<td[^>]*colspan=\"\d+\"[^>]*>\s*(?:#+\s*)?([IVXLCDM\d]+\.[^<]{1,100})\s*</td>\s*</tr>",
        r"\n\n## \1\n\n",
        text,
        flags=re.IGNORECASE,
    )

    # 2. Fix font encoding spacing errors for key structural words
    # (e.g. M U C -> MỤC, D I E U -> ĐIỀU, C H U O N G -> CHƯƠNG)
    # This is common in some PDF encoders (like Prudential in our dataset).
    replacements = {
        r"\bM\s*[Ụụ]\s*C\s*L\s*[Ụụ]\s*C\b": "Mục lục",
        r"\bM\s*[Ụụ]\s*C\b": "Mục",
        r"\bC\s*H\s*[Ưư]\s*[Ơơ]\s*N\s*G\b": "Chương",
        r"\b[Đđ]\s*I\s*[ÊêỀềỂểỄễẾếỆệ]\s*U\b": "Điều",
        r"\bK\s*H\s*O\s*[ẢảẨẩẤấẪẫẬậ]\s*N\b": "Khoản",
        r"\b[Đđ]\s*I\s*[ỂểỀềỂểỄễẾếỆệ]\s*M\b": "Điểm",
        r"\bP\s*H\s*[ẦầẤấẨẩẪẫẬậ]\s*N\b": "Phần",
        r"\bP\s*H\s*U\s*[LụLu]\s*U\s*C\b": "Phụ lục",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(
            pattern,
            lambda m, rep=replacement: _fix_case(m.group(0), rep),
            text,
            flags=re.IGNORECASE,
        )

    # Merge Chapter/Part/Section/Article/Appendix titles written on the next line (common in laws)
    # e.g.
    # ## Chương I
    # NHỮNG QUY ĐỊNH CHUNG
    # -> ## Chương I. NHỮNG QUY ĐỊNH CHUNG
    text = re.sub(
        r"(^\s*(?:#+\s*)?(?:Phần|Chương|Mục|Điều|Phụ\s*lục)\s+[IVXLCDM\d]+[a-z]?)\s*\n\s*([^#\n\d\s][^\n]{1,100})\b",
        r"\1. \2",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # 3. Clean double spaces and spaces before punctuation
    text = re.sub(r"[ \t]+", " ", text)  # Collapse spaces/tabs
    text = re.sub(r"\s+([.,;:?])", r"\1", text)  # Remove space before punctuation

    # 4. Fix wrap-around lines for headings (e.g. headings split across newlines)
    # If a line starts with a number like "1.2" but the heading text is wrapped
    # to the next line, we want to merge them if the next line looks like a heading continuation.
    # Note: MinerU layout analysis usually handles this, but we do a simple fallback if needed.

    # 5. Remove standard watermark patterns or empty page markers if any
    # (MinerU already filters headers/footers, but we ensure no trash is left)
    text = re.sub(r"-+\s*Trang\s*\d+\s*/\s*\d+\s*-+", "", text, flags=re.IGNORECASE)

    return text.strip()


def clean_document(doc: ExtractedDocument) -> ExtractedDocument:
    """Clean all page text contents inside the document."""
    cleaned_pages = []
    for page in doc.pages:
        cleaned_text = clean_text_content(page.text)
        cleaned_pages.append(ExtractedPage(page_index=page.page_index, text=cleaned_text))

    # Return a new ExtractedDocument with cleaned pages
    return ExtractedDocument(
        pages=cleaned_pages, metadata=doc.metadata, ocr_used=doc.ocr_used, extractor=doc.extractor
    )
