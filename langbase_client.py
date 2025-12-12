"""Langbase API client for meeting summary generation."""

import json
import time
import requests
from typing import Optional, List

from prompts import (
    MEETING_SUMMARY_SYSTEM_PROMPT,
    CHUNK_ANALYSIS_PROMPT,
    MERGE_SUMMARIES_PROMPT,
    get_meeting_summary_prompt,
    get_chunk_analysis_prompt,
    get_merge_summaries_prompt
)


class LangbaseClient:
    """Client for interacting with Langbase REST API."""

    BASE_URL = "https://api.langbase.com/v1/pipes/run"
    DEFAULT_TIMEOUT = 120  # seconds (increased for longer processing)
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, api_key: str, pipe_name: str = "meeting-summary", temperature: float = 0.3):
        """
        Initialize the Langbase client.

        Args:
            api_key: Langbase API key for authentication
            pipe_name: Name of the Langbase pipe to use
            temperature: LLM temperature (0.0-1.0), lower = more consistent
        """
        self.api_key = api_key
        self.pipe_name = pipe_name
        self.temperature = temperature
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def summarize_meeting(self, transcript: str, meeting_type: Optional[str] = None) -> dict:
        """
        Send transcript to Langbase and return parsed summary.

        Args:
            transcript: Raw meeting transcript text
            meeting_type: Type of meeting (e.g., 'standup', 'retrospective')

        Returns:
            Parsed JSON summary dict

        Raises:
            Exception: On API errors, network issues, or JSON parsing failures
        """
        # Use meeting-type-specific prompt if provided, otherwise use generic
        system_prompt = get_meeting_summary_prompt(meeting_type)

        payload = {
            "name": self.pipe_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ],
            "model": "openai:gpt-4o",
            "stream": False,
            "temperature": self.temperature,
            "max_tokens": 4000  # Ensure enough output space for complete JSON
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=self.DEFAULT_TIMEOUT
            )

            if response.status_code != 200:
                error_msg = self._extract_error_message(response)
                raise Exception(f"API error ({response.status_code}): {error_msg}")

            response_data = response.json()
            content = self._extract_content(response_data)

            if not content:
                raise Exception("Empty response from API")

            return self._parse_llm_json(content)

        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The transcript may be too long. Please try with a shorter transcript.")
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to connect to the API. Please check your internet connection.")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response: {str(e)}")

    def _extract_error_message(self, response: requests.Response) -> str:
        """Extract error message from API response."""
        try:
            error_data = response.json()
            return error_data.get("error", {}).get("message", response.text)
        except:
            return response.text

    def _extract_content(self, response_data: dict) -> Optional[str]:
        """Extract content from Langbase API response."""
        # Handle standard OpenAI-style response format
        if "choices" in response_data:
            choices = response_data.get("choices", [])
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                return message.get("content", "")

        # Handle direct content response
        if "content" in response_data:
            return response_data["content"]

        # Handle completion field
        if "completion" in response_data:
            return response_data["completion"]

        return None

    def _parse_llm_json(self, response_text: str) -> dict:
        """
        Parse JSON from LLM response, handling markdown code blocks and truncation.

        Args:
            response_text: Raw text response from LLM

        Returns:
            Parsed JSON dict

        Raises:
            Exception: If JSON parsing fails
        """
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Try to repair truncated JSON
            repaired = self._try_repair_json(text)
            if repaired:
                return repaired

            # Provide helpful error context
            error_context = self._get_json_error_context(text, e)
            raise Exception(
                f"Failed to parse summary JSON: {str(e)}. {error_context}\n"
                "This usually happens when the AI response was truncated. "
                "Try with a shorter transcript or try again."
            )

    def _get_json_error_context(self, text: str, error: json.JSONDecodeError) -> str:
        """
        Get helpful context about a JSON parsing error.

        Args:
            text: The JSON text that failed to parse
            error: The JSONDecodeError exception

        Returns:
            A helpful context string
        """
        # Check for common issues
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')

        issues = []
        if open_braces > 0:
            issues.append(f"{open_braces} unclosed braces")
        if open_brackets > 0:
            issues.append(f"{open_brackets} unclosed brackets")

        # Check if we're likely truncated mid-string
        if "Unterminated string" in str(error):
            issues.append("unterminated string (response likely cut off mid-text)")

        if issues:
            return f"Issues detected: {', '.join(issues)}."
        return "The AI response may be malformed."

    def _try_repair_json(self, text: str) -> Optional[dict]:
        """
        Attempt to repair truncated or malformed JSON.

        Args:
            text: Malformed JSON string

        Returns:
            Parsed dict if repair successful, None otherwise
        """
        import re

        # Strategy 1: Fix unterminated strings first
        # This handles cases where LLM output was cut off mid-string
        repaired_text = self._fix_unterminated_strings(text)

        # Strategy 2: Try to close unclosed brackets/braces
        open_braces = repaired_text.count('{') - repaired_text.count('}')
        open_brackets = repaired_text.count('[') - repaired_text.count(']')

        # If we have unclosed structures, try to close them
        if open_braces > 0 or open_brackets > 0:
            repair_attempts = [
                # Try with repaired text
                repaired_text + ']' * open_brackets + '}' * open_braces,
                # Trim to last complete array item or object property
                repaired_text.rsplit(',', 1)[0] + ']' * open_brackets + '}' * open_braces,
                # Trim to last complete string value
                repaired_text.rsplit('",', 1)[0] + '"]' * min(1, open_brackets) + '}' * open_braces,
                # Trim to second-to-last comma (in case the last item is incomplete)
                self._trim_to_last_complete_item(repaired_text) + ']' * open_brackets + '}' * open_braces,
            ]

            for attempt in repair_attempts:
                try:
                    # Clean up potential issues
                    attempt = attempt.replace(',]', ']').replace(',}', '}')
                    attempt = re.sub(r',\s*]', ']', attempt)
                    attempt = re.sub(r',\s*}', '}', attempt)
                    result = json.loads(attempt)
                    return result
                except json.JSONDecodeError:
                    continue

        # Strategy 3: Try to find valid JSON substring
        start = text.find('{')
        if start != -1:
            depth = 0
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i+1])
                        except json.JSONDecodeError:
                            break

        return None

    def _fix_unterminated_strings(self, text: str) -> str:
        """
        Fix unterminated strings in JSON by finding unclosed quotes.

        Args:
            text: JSON string that may have unterminated strings

        Returns:
            Repaired JSON string
        """
        # Track if we're inside a string
        in_string = False
        escape_next = False
        last_string_start = -1
        result = list(text)

        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue

            if char == '\\' and in_string:
                escape_next = True
                continue

            if char == '"':
                if in_string:
                    in_string = False
                else:
                    in_string = True
                    last_string_start = i

        # If we ended inside a string, close it
        if in_string and last_string_start != -1:
            # Find a good place to close - look for common truncation patterns
            # Truncate any obviously incomplete content at the end
            truncate_point = len(text)

            # Look for incomplete escape sequences at the end
            if text.endswith('\\'):
                truncate_point = len(text) - 1

            # Close the string
            result = text[:truncate_point]
            # Remove any trailing partial content that looks incomplete
            result = result.rstrip()
            if result.endswith(','):
                result = result[:-1]
            result = result + '"'
            return result

        return text

    def _trim_to_last_complete_item(self, text: str) -> str:
        """
        Trim JSON text to the last complete object or array item.

        Args:
            text: Potentially truncated JSON text

        Returns:
            Trimmed text ending at a complete item
        """
        # Find the last occurrence of common item terminators
        # These indicate the end of a complete value
        terminators = ['"},', '"],', '"},\n', '"],\n', '"\n    },', '"\n  },']

        best_pos = -1
        best_terminator = ''

        for term in terminators:
            pos = text.rfind(term)
            if pos > best_pos:
                best_pos = pos
                best_terminator = term

        if best_pos > 0:
            return text[:best_pos + len(best_terminator)].rstrip(',').rstrip()

        return text

    def _make_request_with_retry(self, payload: dict) -> dict:
        """
        Make API request with retry logic for transient failures.

        Args:
            payload: Request payload

        Returns:
            Parsed response data

        Raises:
            Exception: On persistent API errors
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.post(
                    self.BASE_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=self.DEFAULT_TIMEOUT
                )

                if response.status_code == 200:
                    response_data = response.json()
                    content = self._extract_content(response_data)
                    if not content:
                        raise Exception("Empty response from API")
                    return self._parse_llm_json(content)

                # Check if error is retryable (rate limits, server errors)
                if response.status_code in (429, 500, 502, 503, 504):
                    last_error = f"API error ({response.status_code}): {self._extract_error_message(response)}"
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                        continue

                # Non-retryable error
                error_msg = self._extract_error_message(response)
                raise Exception(f"API error ({response.status_code}): {error_msg}")

            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                raise Exception("Request timed out after multiple retries. The content may be too long.")

            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                raise Exception("Unable to connect to the API after multiple retries.")

        raise Exception(f"Failed after {self.MAX_RETRIES} retries. Last error: {last_error}")

    def process_chunk(
        self,
        chunk_text: str,
        chunk_number: int,
        total_chunks: int,
        meeting_type: Optional[str] = None
    ) -> dict:
        """
        Process a single transcript chunk with enhanced extraction.

        Args:
            chunk_text: The chunk text to analyze
            chunk_number: Which chunk this is (1-indexed)
            total_chunks: Total number of chunks
            meeting_type: Type of meeting (e.g., 'standup', 'retrospective')

        Returns:
            Parsed chunk analysis dict
        """
        # Use meeting-type-specific prompt if provided
        if meeting_type:
            system_prompt = get_chunk_analysis_prompt(chunk_number, total_chunks, meeting_type)
        else:
            system_prompt = CHUNK_ANALYSIS_PROMPT.format(
                chunk_number=chunk_number,
                total_chunks=total_chunks
            )

        payload = {
            "name": self.pipe_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk_text}
            ],
            "stream": False,
            "temperature": self.temperature,
            "max_tokens": 4000  # Ensure enough output space
        }

        return self._make_request_with_retry(payload)

    def merge_summaries(
        self,
        chunk_results: List[dict],
        meeting_type: Optional[str] = None
    ) -> dict:
        """
        Merge multiple chunk summaries into a final comprehensive summary.

        Args:
            chunk_results: List of parsed chunk analysis dicts
            meeting_type: Type of meeting (e.g., 'standup', 'retrospective')

        Returns:
            Merged final summary dict
        """
        # Format chunk summaries for the merge prompt
        chunks_text = ""
        for i, result in enumerate(chunk_results, 1):
            chunks_text += f"\n\n=== CHUNK {i} OF {len(chunk_results)} ===\n"
            chunks_text += json.dumps(result, indent=2)

        # Use meeting-type-specific prompt if provided
        system_prompt = get_merge_summaries_prompt(meeting_type) if meeting_type else MERGE_SUMMARIES_PROMPT

        payload = {
            "name": self.pipe_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Merge these {len(chunk_results)} chunk summaries into a final meeting summary:{chunks_text}"}
            ],
            "stream": False,
            "temperature": self.temperature,
            "max_tokens": 4000  # Ensure enough output space
        }

        return self._make_request_with_retry(payload)
