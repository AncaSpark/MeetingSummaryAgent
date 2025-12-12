"""Transcript chunking engine for processing long meetings."""

import re
from dataclasses import dataclass
from typing import List, Set


@dataclass
class Chunk:
    """Represents a chunk of transcript text."""
    text: str
    start_idx: int
    end_idx: int
    speakers: Set[str]
    chunk_number: int
    total_chunks: int


class TranscriptChunker:
    """Splits long transcripts into manageable chunks for processing."""

    # Approximate characters per token (conservative estimate)
    CHARS_PER_TOKEN = 4
    # Default max tokens per chunk
    DEFAULT_MAX_TOKENS = 3000
    # Overlap tokens between chunks for context continuity
    OVERLAP_TOKENS = 200

    # Pattern to detect speaker turns (e.g., "John:", "Sarah (PM):", "Dr. Smith:")
    SPEAKER_PATTERN = re.compile(r'^([A-Z][a-zA-Z\s\.\-]+(?:\s*\([^)]+\))?)\s*:', re.MULTILINE)

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, overlap_tokens: int = OVERLAP_TOKENS):
        """
        Initialize the chunker.

        Args:
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.max_chars = max_tokens * self.CHARS_PER_TOKEN
        self.overlap_chars = overlap_tokens * self.CHARS_PER_TOKEN

    def chunk(self, transcript: str) -> List[Chunk]:
        """
        Split transcript into chunks.

        Args:
            transcript: Full meeting transcript text

        Returns:
            List of Chunk objects
        """
        transcript = transcript.strip()

        # If transcript fits in one chunk, return as single chunk
        if len(transcript) <= self.max_chars:
            speakers = self._extract_speakers(transcript)
            return [Chunk(
                text=transcript,
                start_idx=0,
                end_idx=len(transcript),
                speakers=speakers,
                chunk_number=1,
                total_chunks=1
            )]

        # Split by speaker turns first
        chunks = self._split_by_speakers(transcript)

        # If any chunk is still too large, split further by paragraphs
        final_chunks = []
        for chunk_text in chunks:
            if len(chunk_text) > self.max_chars:
                sub_chunks = self._split_by_paragraphs(chunk_text)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk_text)

        # Merge very small chunks with neighbors
        merged_chunks = self._merge_small_chunks(final_chunks)

        # Add overlap between chunks for context
        overlapped_chunks = self._add_overlap(merged_chunks, transcript)

        # Build final Chunk objects
        return self._build_chunk_objects(overlapped_chunks, transcript)

    def _split_by_speakers(self, transcript: str) -> List[str]:
        """Split transcript by speaker turns, grouping turns to fit max size."""
        # Find all speaker turn positions
        matches = list(self.SPEAKER_PATTERN.finditer(transcript))

        if not matches:
            # No speaker patterns found, fall back to paragraph splitting
            return self._split_by_paragraphs(transcript)

        # Extract turn boundaries
        turn_positions = [m.start() for m in matches]
        turn_positions.append(len(transcript))  # Add end position

        # Group turns into chunks
        chunks = []
        current_chunk_start = 0
        current_chunk_text = ""

        for i in range(len(turn_positions) - 1):
            turn_start = turn_positions[i]
            turn_end = turn_positions[i + 1]
            turn_text = transcript[turn_start:turn_end]

            # Check if adding this turn would exceed max size
            if len(current_chunk_text) + len(turn_text) > self.max_chars:
                # Save current chunk if it has content
                if current_chunk_text:
                    chunks.append(current_chunk_text.strip())
                current_chunk_text = turn_text
                current_chunk_start = turn_start
            else:
                current_chunk_text += turn_text

        # Don't forget the last chunk
        if current_chunk_text:
            chunks.append(current_chunk_text.strip())

        return chunks

    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraph breaks when speaker splitting isn't enough."""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 > self.max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If single paragraph is too large, split by sentences
                if len(para) > self.max_chars:
                    sentence_chunks = self._split_by_sentences(para)
                    chunks.extend(sentence_chunks[:-1])
                    current_chunk = sentence_chunks[-1] if sentence_chunks else ""
                else:
                    current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _split_by_sentences(self, text: str) -> List[str]:
        """Last resort: split by sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > self.max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _merge_small_chunks(self, chunks: List[str], min_size: int = 500) -> List[str]:
        """Merge chunks that are too small with their neighbors."""
        if len(chunks) <= 1:
            return chunks

        merged = []
        i = 0

        while i < len(chunks):
            current = chunks[i]

            # If current chunk is small and there's a next chunk, try to merge
            while len(current) < min_size and i + 1 < len(chunks):
                next_chunk = chunks[i + 1]
                if len(current) + len(next_chunk) + 2 <= self.max_chars:
                    current = current + "\n\n" + next_chunk
                    i += 1
                else:
                    break

            merged.append(current)
            i += 1

        return merged

    def _add_overlap(self, chunks: List[str], original: str) -> List[str]:
        """Add overlapping context between chunks."""
        if len(chunks) <= 1:
            return chunks

        overlapped = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk: no prefix overlap needed
                overlapped.append(chunk)
            else:
                # Add context from previous chunk
                prev_chunk = chunks[i - 1]
                overlap_text = self._get_overlap_suffix(prev_chunk)
                if overlap_text:
                    overlapped.append(f"[...continued from previous section...]\n{overlap_text}\n\n{chunk}")
                else:
                    overlapped.append(chunk)

        return overlapped

    def _get_overlap_suffix(self, text: str) -> str:
        """Get the last portion of text for overlap context."""
        if len(text) <= self.overlap_chars:
            return text

        # Try to break at a speaker turn or paragraph
        suffix = text[-self.overlap_chars:]

        # Find a good break point (speaker turn or paragraph)
        speaker_match = self.SPEAKER_PATTERN.search(suffix)
        if speaker_match:
            return suffix[speaker_match.start():]

        # Fall back to paragraph break
        para_break = suffix.find('\n\n')
        if para_break != -1:
            return suffix[para_break + 2:]

        return suffix

    def _build_chunk_objects(self, chunk_texts: List[str], original: str) -> List[Chunk]:
        """Build Chunk dataclass objects with metadata."""
        total = len(chunk_texts)
        chunks = []

        for i, text in enumerate(chunk_texts):
            # Find approximate position in original (for reference)
            # Note: positions are approximate due to overlap additions
            clean_text = text.replace("[...continued from previous section...]\n", "")
            start_idx = original.find(clean_text[:100]) if len(clean_text) >= 100 else original.find(clean_text)
            start_idx = max(0, start_idx)

            chunks.append(Chunk(
                text=text,
                start_idx=start_idx,
                end_idx=min(start_idx + len(text), len(original)),
                speakers=self._extract_speakers(text),
                chunk_number=i + 1,
                total_chunks=total
            ))

        return chunks

    def _extract_speakers(self, text: str) -> Set[str]:
        """Extract unique speaker names from text."""
        matches = self.SPEAKER_PATTERN.findall(text)
        # Clean up speaker names (remove roles in parentheses for dedup)
        speakers = set()
        for match in matches:
            # Extract just the name part
            name = re.sub(r'\s*\([^)]+\)\s*', '', match).strip()
            if name:
                speakers.add(name)
        return speakers


def estimate_chunks(transcript: str, max_tokens: int = 3000) -> int:
    """
    Estimate how many chunks a transcript will produce.

    Args:
        transcript: The transcript text
        max_tokens: Maximum tokens per chunk

    Returns:
        Estimated number of chunks
    """
    chars_per_token = 4
    max_chars = max_tokens * chars_per_token
    return max(1, (len(transcript) + max_chars - 1) // max_chars)
