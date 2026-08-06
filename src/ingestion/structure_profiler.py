import re

from loguru import logger

from src.ingestion.models import (DocumentProfile, ExtractedDocument,
                                  HeadingMatch)


class StructureProfileError(Exception):
    """Raised when the document structure profiling fails or confidence is too low."""

    pass


class DocumentStructureProfiler:
    """DocumentStructureProfiler handles Layer 2 structure understanding.
    It identifies headings, infers hierarchical relations, and evaluates outline confidence.
    """

    # Heading patterns with support for optional markdown hashes (#)
    PATTERNS = {
        "PHAN": re.compile(
            r"^\s*(?:#+\s*)?(?:PHẦN|Phần)\s+([A-Z\dIVX]+)\b.*$", re.MULTILINE | re.IGNORECASE
        ),
        "CHUONG": re.compile(
            r"^\s*(?:#+\s*)?(?:CHƯƠNG|Chương)\s+([IVXLCDM\d]+)\b.*$", re.MULTILINE | re.IGNORECASE
        ),
        "MUC": re.compile(
            r"^\s*(?:#+\s*)?(?:MỤC|Mục)\s+([IVXLCDM\d]+|[A-Z\d]+)\b.*$",
            re.MULTILINE | re.IGNORECASE,
        ),
        "DIEU": re.compile(
            r"^\s*(?:#+\s*)?(?:ĐIỀU|Điều)\s+(\d+)\b.*$", re.MULTILINE | re.IGNORECASE
        ),
        "KHOAN": re.compile(r"^\s*(?:#+\s*)?(\d+)\.\s+.*$", re.MULTILINE),
        "ROMAN": re.compile(r"^\s*(?:#+\s*)?([IVXLCDM]+)\.\s+.*$", re.MULTILINE),
        "DECIMAL": re.compile(r"^\s*(?:#+\s*)?(\d+(?:\.\d+)+)\.?\s+.*$", re.MULTILINE),
    }

    # Standard order from high level to low level (tie breaker)
    STANDARD_ORDER = ["PHAN", "CHUONG", "MUC", "DIEU", "ROMAN", "KHOAN", "DECIMAL"]

    def __init__(self, min_confidence: float = 0.6):
        self.min_confidence = min_confidence

    def _get_page_index(self, char_idx: int, page_offsets: list[tuple[int, int, int]]) -> int:
        """Map absolute char index in full text back to the page index."""
        for start, end, page_idx in page_offsets:
            if start <= char_idx <= end:
                return page_idx
        return page_offsets[-1][2] if page_offsets else 0

    def find_headings(self, doc: ExtractedDocument) -> list[HeadingMatch]:
        """Detect all structural headings inside the document and map to page numbers."""
        full_text = ""
        page_offsets = []
        for page in doc.pages:
            start_idx = len(full_text)
            full_text += page.text + "\n"
            end_idx = len(full_text)
            page_offsets.append((start_idx, end_idx, page.page_index))

        headings = []
        for name, pattern in self.PATTERNS.items():
            for match in pattern.finditer(full_text):
                start = match.start()
                end = match.end()
                match_text = match.group(0).strip()
                page_idx = self._get_page_index(start, page_offsets)
                headings.append(
                    HeadingMatch(
                        pattern_type=name,
                        match_text=match_text,
                        start_idx=start,
                        end_idx=end,
                        page_index=page_idx,
                    )
                )

        # Sort headings by their start index to preserve document order
        headings.sort(key=lambda x: x.start_idx)
        return headings

    def calculate_confidence(self, headings: list[HeadingMatch], text_len: int) -> float:
        """Calculate confidence score of the structure detection."""
        if not headings:
            return 0.0

        counts = {}
        for h in headings:
            counts[h.pattern_type] = counts.get(h.pattern_type, 0) + 1

        # If document is long but has almost no outline anchors
        if text_len > 3000 and len(headings) < 2:
            return 0.1

        # Check sequence of DIEU matches
        dieu_matches = [h for h in headings if h.pattern_type == "DIEU"]
        if len(dieu_matches) > 1:
            nums = []
            for m in dieu_matches:
                # Find number inside text (e.g. Điều 4 -> 4)
                num_match = re.search(r"\d+", m.match_text)
                if num_match:
                    nums.append(int(num_match.group()))

            if len(nums) > 1:
                consecutive = 0
                for i in range(len(nums) - 1):
                    diff = nums[i + 1] - nums[i]
                    # consecutiveness check (difference is 1, or reset to 1 for chapters)
                    if diff == 1 or nums[i + 1] == 1:
                        consecutive += 1
                seq_ratio = consecutive / (len(nums) - 1)
                return round(0.4 + 0.6 * seq_ratio, 2)

        return (
            0.8  # Default high score if document outline has matches but no sequential Dieu check
        )

    def determine_profile_type(self, levels: list[str]) -> str:
        """Determine structure profile type based on identified levels."""
        levels_set = set(levels)
        if "CHUONG" in levels_set and "DIEU" in levels_set:
            return "chapter_article"
        elif "PHAN" in levels_set and "DIEU" in levels_set:
            return "part_article"
        elif "DIEU" in levels_set and "DECIMAL" in levels_set:
            return "article_decimal"
        elif "DIEU" in levels_set and "KHOAN" in levels_set:
            return "article_clause"
        elif "DIEU" in levels_set:
            return "article_only"
        elif "DECIMAL" in levels_set:
            return "decimal_only"
        return "generic_outline"

    def profile_document(
        self, doc: ExtractedDocument
    ) -> tuple[DocumentProfile, list[HeadingMatch]]:
        """Profile the document structure.

        Raises:
            StructureProfileError: If the outline confidence is below the threshold (FR-004).
        """
        full_text = doc.get_full_text()
        headings = self.find_headings(doc)

        # Calculate pattern counts
        pattern_counts = {}
        for h in headings:
            pattern_counts[h.pattern_type] = pattern_counts.get(h.pattern_type, 0) + 1

        # Infer hierarchical levels using Frequency-based sorting
        # Patterns with lower frequency are placed at higher levels
        # If frequencies are equal, we sort using the STANDARD_ORDER list index
        active_patterns = list(pattern_counts.keys())

        # Custom sorting key prioritizing standard conventions to avoid count anomalies on short texts
        def sort_key(name):
            try:
                return self.STANDARD_ORDER.index(name)
            except ValueError:
                return 99

        active_patterns.sort(key=sort_key)
        levels = active_patterns

        # Calculate outline confidence
        confidence = self.calculate_confidence(headings, len(full_text))

        # Reject document if outline profiling confidence is too low
        if confidence < self.min_confidence:
            logger.error(
                f"Structure profiling rejected for {doc.metadata.source_file} (Confidence: {confidence:.2f} < {self.min_confidence:.2f})"
            )
            raise StructureProfileError(
                f"Tài liệu '{doc.metadata.source_file}' có cấu trúc không đồng nhất hoặc bị lỗi trích xuất tiêu đề nghiêm trọng "
                f"(Độ tin cậy: {confidence:.2f} < {self.min_confidence:.2f})."
            )

        profile_type = self.determine_profile_type(levels)

        profile = DocumentProfile(
            profile_type=profile_type,
            levels=levels,
            confidence=confidence,
            pattern_counts=pattern_counts,
        )

        logger.info(
            f"Structure profiled successfully: {profile_type} (Levels: {levels}, Confidence: {confidence})"
        )
        return profile, headings
