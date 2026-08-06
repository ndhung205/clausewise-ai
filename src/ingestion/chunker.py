from loguru import logger

from src.ingestion.models import (Chunk, DocumentProfile, ExtractedDocument,
                                  HeadingMatch)


class AdaptiveChunker:
    """AdaptiveChunker handles Layer 2 clause-aware chunking.
    It splits the document using structural headings and generates chunks with 13 metadata fields.
    """

    def __init__(
        self, max_chunk_size: int = 2000, sub_chunk_size: int = 1000, sub_chunk_overlap: int = 150
    ):
        self.max_chunk_size = max_chunk_size
        self.sub_chunk_size = sub_chunk_size
        self.sub_chunk_overlap = sub_chunk_overlap

    def _get_page_index_for_char(
        self, char_idx: int, page_offsets: list[tuple[int, int, int]]
    ) -> int:
        """Map absolute char index in full text back to the page index."""
        for start, end, page_idx in page_offsets:
            if start <= char_idx <= end:
                return page_idx
        return page_offsets[-1][2] if page_offsets else 0

    def chunk_document(
        self, doc: ExtractedDocument, profile: DocumentProfile, headings: list[HeadingMatch]
    ) -> list[Chunk]:
        """Split the document into clause-aware chunks using structural headings and hierarchy."""
        full_text = doc.get_full_text()

        # Build page offsets to calculate page_start and page_end for chunks
        page_offsets = []
        current_len = 0
        for page in doc.pages:
            start_idx = current_len
            current_len += len(page.text) + 1  # accounts for '\n' separator
            page_offsets.append((start_idx, current_len, page.page_index))

        # If no headings are found, fallback to fixed-size chunking for the entire document
        if not headings:
            logger.warning(
                f"No headings found for document {doc.metadata.source_file}. Falling back to fixed-size chunking."
            )
            return self._fallback_fixed_size(doc, profile, page_offsets)

        chunks = []
        levels = (
            profile.levels
        )  # hierarchical order from high to low (e.g. ["PHAN", "DIEU", "DECIMAL"])
        active_headings = {}  # maintains the current active heading for each pattern type

        # Add a dummy final segment boundary
        boundaries = headings + [
            HeadingMatch(
                pattern_type="EOF",
                match_text="",
                start_idx=len(full_text),
                end_idx=len(full_text),
                page_index=doc.pages[-1].page_index if doc.pages else 0,
            )
        ]

        for idx in range(len(boundaries) - 1):
            h_curr = boundaries[idx]
            h_next = boundaries[idx + 1]

            # 1. Update active headings hierarchy path
            curr_type = h_curr.pattern_type
            if curr_type in levels:
                type_idx = levels.index(curr_type)
                # Clear all active headings at lower levels (larger indices in levels list)
                for lower_type in levels[type_idx + 1 :]:
                    if lower_type in active_headings:
                        del active_headings[lower_type]
                active_headings[curr_type] = h_curr.match_text
            else:
                # If pattern type is not in inferred levels (e.g., custom outlier), treat as leaf node
                active_headings[curr_type] = h_curr.match_text

            # Construct hierarchy path (e.g., "CHƯƠNG I / Điều 3 / 3.1")
            path_parts = []
            for lvl in levels:
                if lvl in active_headings:
                    path_parts.append(active_headings[lvl])
            # Include current heading if it's not already in levels or path
            if h_curr.match_text not in path_parts:
                path_parts.append(h_curr.match_text)

            hierarchy_path = " / ".join(path_parts)

            # 2. Extract segment text
            segment_start = h_curr.start_idx
            segment_end = h_next.start_idx
            segment_text = full_text[segment_start:segment_end].strip()

            if not segment_text:
                continue

            # Determine page bounds
            page_start = h_curr.page_index
            page_end = self._get_page_index_for_char(segment_end - 1, page_offsets)

            # 3. Handle large segments with fallback sub-chunking
            if len(segment_text) > self.max_chunk_size:
                logger.info(
                    f"Segment '{h_curr.match_text}' is too large ({len(segment_text)} chars). Splitting with sub-chunking."
                )
                sub_chunks = self._split_segment(segment_text, h_curr.match_text)
                for s_idx, sub_text in enumerate(sub_chunks):
                    chunks.append(
                        Chunk(
                            text=sub_text,
                            source_file=doc.metadata.source_file,
                            company=doc.metadata.company,
                            product=doc.metadata.product,
                            document_type=doc.metadata.document_type,
                            page_start=page_start,
                            page_end=page_end,
                            hierarchy_path=f"{hierarchy_path} [Phần {s_idx + 1}]",
                            section=h_curr.match_text,
                            extractor=doc.extractor,
                            profile_type=profile.profile_type,
                            hierarchy_confidence=profile.confidence,
                            ocr_used=doc.ocr_used,
                            parser_version="1.0.0",
                        )
                    )
            else:
                chunks.append(
                    Chunk(
                        text=segment_text,
                        source_file=doc.metadata.source_file,
                        company=doc.metadata.company,
                        product=doc.metadata.product,
                        document_type=doc.metadata.document_type,
                        page_start=page_start,
                        page_end=page_end,
                        hierarchy_path=hierarchy_path,
                        section=h_curr.match_text,
                        extractor=doc.extractor,
                        profile_type=profile.profile_type,
                        hierarchy_confidence=profile.confidence,
                        ocr_used=doc.ocr_used,
                        parser_version="1.0.0",
                    )
                )

        logger.info(f"Created {len(chunks)} chunks for {doc.metadata.source_file}.")
        return chunks

    def _split_segment(self, text: str, heading_text: str) -> list[str]:
        """Split a long segment using fixed-size chunking, prepending the heading to each chunk."""
        sub_chunks = []
        start = 0
        while start < len(text):
            end = start + self.sub_chunk_size
            chunk_content = text[start:end]

            # Prepend heading if this is a sub-chunk (so RAG retains context)
            if start > 0:
                chunk_text = f"[{heading_text} - Tiếp theo]\n{chunk_content}"
            else:
                chunk_text = chunk_content

            sub_chunks.append(chunk_text)
            start += self.sub_chunk_size - self.sub_chunk_overlap
        return sub_chunks

    def _fallback_fixed_size(
        self,
        doc: ExtractedDocument,
        profile: DocumentProfile,
        page_offsets: list[tuple[int, int, int]],
    ) -> list[Chunk]:
        """Fallback chunker if no headings were found in the document structure."""
        full_text = doc.get_full_text()
        chunks = []

        start = 0
        chunk_idx = 1
        while start < len(full_text):
            end = start + self.sub_chunk_size
            chunk_text = full_text[start:end]

            page_start = self._get_page_index_for_char(start, page_offsets)
            page_end = self._get_page_index_for_char(min(end - 1, len(full_text) - 1), page_offsets)

            chunks.append(
                Chunk(
                    text=chunk_text,
                    source_file=doc.metadata.source_file,
                    company=doc.metadata.company,
                    product=doc.metadata.product,
                    document_type=doc.metadata.document_type,
                    page_start=page_start,
                    page_end=page_end,
                    hierarchy_path=f"Văn bản / Chunk {chunk_idx}",
                    section="N/A",
                    extractor=doc.extractor,
                    profile_type=profile.profile_type,
                    hierarchy_confidence=profile.confidence,
                    ocr_used=doc.ocr_used,
                    parser_version="1.0.0",
                )
            )
            start += self.sub_chunk_size - self.sub_chunk_overlap
            chunk_idx += 1

        return chunks
