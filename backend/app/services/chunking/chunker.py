"""
Markdown chunking service.
"""
from typing import List, Dict, Any
import re


class MarkdownChunker:
    """Markdown chunker with heading-aware splitting."""

    def __init__(
        self,
        chunk_size: int = 750,
        overlap: int = 100,
        max_tokens: int = 1000,
        min_tokens: int = 500
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens

    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk markdown text with heading awareness."""
        chunks = []

        # Split by headings
        sections = self._split_by_headings(text)

        # Chunk each section
        for section in sections:
            section_chunks = self._chunk_section(section, metadata)
            chunks.extend(section_chunks)

        return chunks

    def _split_by_headings(self, text: str) -> List[Dict[str, Any]]:
        """Split text by markdown headings."""
        sections = []
        current_section = {"heading": "", "content": ""}

        lines = text.split("\n")
        for line in lines:
            if line.startswith("#"):
                # Save current section if it has content
                if current_section["content"]:
                    sections.append(current_section)
                # Start new section
                current_section = {
                    "heading": line.strip(),
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"

        # Add last section
        if current_section["content"]:
            sections.append(current_section)

        return sections

    def _chunk_section(
        self,
        section: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk a section into smaller pieces."""
        content = section["content"]
        heading = section["heading"]

        chunks = []
        start = 0
        content_length = len(content)

        while start < content_length:
            end = start + self.chunk_size
            chunk_content = content[start:end]

            # Add overlap for next chunk
            if end < content_length:
                start = end - self.overlap
            else:
                start = end

            # Create chunk with metadata
            chunk_metadata = {
                **metadata,
                "heading": heading,
                "chunk_start": start,
                "chunk_end": end
            }

            chunks.append({
                "content": chunk_content,
                "metadata": chunk_metadata
            })

        return chunks

    def estimate_token_count(self, text: str) -> int:
        """Estimate token count (rough approximation: 4 chars ≈ 1 token)."""
        return len(text) // 4
