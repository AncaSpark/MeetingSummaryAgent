"""Processing pipeline for meeting transcript analysis."""

from typing import Callable, Optional
from dataclasses import dataclass

from chunking import TranscriptChunker, Chunk, estimate_chunks
from langbase_client import LangbaseClient


@dataclass
class ProcessingResult:
    """Result of pipeline processing."""
    summary: dict
    chunks_processed: int
    was_chunked: bool
    chunk_details: list  # Individual chunk results for debugging


class MeetingPipeline:
    """
    Orchestrates the processing of meeting transcripts.

    Handles chunking, parallel processing, and hierarchical merging
    for long transcripts.
    """

    # Threshold in characters for when to use chunking
    CHUNK_THRESHOLD_CHARS = 8000  # ~2000 tokens

    def __init__(
        self,
        client: LangbaseClient,
        max_tokens_per_chunk: int = 2000,  # Reduced to avoid output truncation
        overlap_tokens: int = 150
    ):
        """
        Initialize the pipeline.

        Args:
            client: Langbase API client
            max_tokens_per_chunk: Maximum tokens per chunk
            overlap_tokens: Overlap between chunks for context
        """
        self.client = client
        self.chunker = TranscriptChunker(
            max_tokens=max_tokens_per_chunk,
            overlap_tokens=overlap_tokens
        )

    def process(
        self,
        transcript: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        force_chunking: bool = False,
        meeting_type: Optional[str] = None
    ) -> ProcessingResult:
        """
        Process a meeting transcript.

        Args:
            transcript: Full meeting transcript text
            progress_callback: Optional callback(current, total, status_message)
            force_chunking: Force chunking even for short transcripts
            meeting_type: Type of meeting (e.g., 'standup', 'retrospective')

        Returns:
            ProcessingResult with summary and metadata
        """
        transcript = transcript.strip()

        # Determine if chunking is needed
        needs_chunking = force_chunking or len(transcript) > self.CHUNK_THRESHOLD_CHARS

        if not needs_chunking:
            # Short transcript - use original single-call approach
            if progress_callback:
                progress_callback(0, 1, "Analyzing transcript...")

            summary = self.client.summarize_meeting(transcript, meeting_type=meeting_type)

            if progress_callback:
                progress_callback(1, 1, "Complete!")

            return ProcessingResult(
                summary=summary,
                chunks_processed=1,
                was_chunked=False,
                chunk_details=[]
            )

        # Long transcript - use chunked processing
        return self._process_chunked(transcript, progress_callback, meeting_type=meeting_type)

    def _process_chunked(
        self,
        transcript: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        meeting_type: Optional[str] = None
    ) -> ProcessingResult:
        """
        Process transcript using chunked approach.

        Args:
            transcript: Full transcript text
            progress_callback: Optional progress callback
            meeting_type: Type of meeting (e.g., 'standup', 'retrospective')

        Returns:
            ProcessingResult with merged summary
        """
        # Step 1: Chunk the transcript
        if progress_callback:
            progress_callback(0, 0, "Splitting transcript into chunks...")

        chunks = self.chunker.chunk(transcript)
        total_steps = len(chunks) + 1  # chunks + merge step

        if progress_callback:
            progress_callback(0, total_steps, f"Processing {len(chunks)} chunks...")

        # Step 2: Process each chunk
        chunk_results = []
        for chunk in chunks:
            if progress_callback:
                progress_callback(
                    chunk.chunk_number,
                    total_steps,
                    f"Analyzing chunk {chunk.chunk_number}/{chunk.total_chunks}..."
                )

            result = self.client.process_chunk(
                chunk_text=chunk.text,
                chunk_number=chunk.chunk_number,
                total_chunks=chunk.total_chunks,
                meeting_type=meeting_type
            )
            chunk_results.append(result)

        # Step 3: Merge results
        if progress_callback:
            progress_callback(len(chunks), total_steps, "Merging summaries...")

        if len(chunk_results) == 1:
            # Single chunk - convert chunk format to final format
            final_summary = self._convert_single_chunk_to_summary(chunk_results[0])
        else:
            # Multiple chunks - use LLM to merge
            final_summary = self.client.merge_summaries(chunk_results, meeting_type=meeting_type)

        if progress_callback:
            progress_callback(total_steps, total_steps, "Complete!")

        return ProcessingResult(
            summary=final_summary,
            chunks_processed=len(chunks),
            was_chunked=True,
            chunk_details=chunk_results
        )

    def _convert_single_chunk_to_summary(self, chunk_result: dict) -> dict:
        """
        Convert single chunk result to final summary format.

        When there's only one chunk, we don't need LLM merging,
        but we need to convert the chunk format to the expected output format.
        """
        # Map chunk format to final summary format
        summary = {
            "tldr": chunk_result.get("chunk_summary", ""),
            "attendees": [],
            "duration_estimate": "Unable to estimate from single segment",
            "topics": chunk_result.get("topics", []),
            "sentiment": chunk_result.get("sentiment", {}),
            "action_items": chunk_result.get("action_items", []),
            "decisions": chunk_result.get("decisions", []),
            "key_topics": [t.get("name", "") for t in chunk_result.get("topics", [])],
            "open_questions": chunk_result.get("open_questions", []),
            "next_steps": chunk_result.get("follow_ups_mentioned", []),
            "notable_quotes": chunk_result.get("key_quotes", [])
        }

        # Convert speaker format
        for speaker in chunk_result.get("speakers", []):
            summary["attendees"].append({
                "name": speaker.get("name", ""),
                "role": speaker.get("role"),
                "contribution_summary": ", ".join(speaker.get("key_contributions", []))
            })

        return summary

    def estimate_processing(self, transcript: str) -> dict:
        """
        Estimate processing requirements for a transcript.

        Args:
            transcript: The transcript text

        Returns:
            Dict with estimation info
        """
        char_count = len(transcript)
        estimated_tokens = char_count // 4
        estimated_chunks = estimate_chunks(transcript, self.chunker.max_tokens)
        will_chunk = char_count > self.CHUNK_THRESHOLD_CHARS

        return {
            "character_count": char_count,
            "estimated_tokens": estimated_tokens,
            "estimated_chunks": estimated_chunks,
            "will_use_chunking": will_chunk,
            "estimated_api_calls": estimated_chunks + (1 if estimated_chunks > 1 else 0)
        }
