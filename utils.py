"""Helper functions for formatting and validation."""

import re
from typing import Tuple


def parse_vtt_timestamp(timestamp: str) -> float:
    """
    Parse a VTT timestamp into seconds.

    Args:
        timestamp: Timestamp string like "00:05:30.500" or "05:30.500"

    Returns:
        Time in seconds
    """
    # Handle both HH:MM:SS.mmm and MM:SS.mmm formats
    parts = timestamp.replace(',', '.').split(':')

    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    elif len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    else:
        return 0.0


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "1 hour 23 minutes" or "45 minutes"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)

    if hours > 0:
        if minutes > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "less than 1 minute"


def parse_vtt(content: str) -> tuple[str, str | None]:
    """
    Parse VTT (WebVTT) content and extract clean transcript text.

    Args:
        content: Raw VTT file content

    Returns:
        Tuple of (clean transcript text, duration string or None)
    """
    lines = content.strip().split('\n')
    transcript_lines = []
    current_speaker = None
    current_text = []

    # Track timestamps for duration
    first_timestamp = None
    last_timestamp = None

    # Patterns
    timestamp_pattern = re.compile(r'^(\d{2}:\d{2}[:\.]?\d{0,2}\.?\d{0,3})\s*-->\s*(\d{2}:\d{2}[:\.]?\d{0,2}\.?\d{0,3})')
    cue_id_pattern = re.compile(r'^\d+$')
    speaker_pattern = re.compile(r'^<v\s+([^>]+)>(.*)$')  # <v Speaker Name>text
    speaker_colon_pattern = re.compile(r'^([A-Z][a-zA-Z\s\.\-]+):\s*(.*)$')  # Speaker: text

    for line in lines:
        line = line.strip()

        # Skip empty lines, WEBVTT header, NOTE comments, STYLE blocks
        if not line:
            continue
        if line.upper().startswith('WEBVTT'):
            continue
        if line.upper().startswith('NOTE'):
            continue
        if line.upper().startswith('STYLE'):
            continue
        if line.startswith('::cue'):
            continue

        # Extract timestamps for duration calculation
        ts_match = timestamp_pattern.match(line)
        if ts_match:
            start_ts = ts_match.group(1)
            end_ts = ts_match.group(2)

            if first_timestamp is None:
                first_timestamp = start_ts
            last_timestamp = end_ts
            continue

        # Skip numeric cue identifiers
        if cue_id_pattern.match(line):
            continue

        # Skip positioning/styling metadata
        if line.startswith('align:') or line.startswith('position:'):
            continue

        # Handle <v Speaker>text format
        speaker_match = speaker_pattern.match(line)
        if speaker_match:
            speaker = speaker_match.group(1).strip()
            text = speaker_match.group(2).strip()

            # Remove closing </v> tag if present
            text = re.sub(r'</v>', '', text).strip()

            if speaker != current_speaker:
                # Save previous speaker's text
                if current_speaker and current_text:
                    transcript_lines.append(f"{current_speaker}: {' '.join(current_text)}")
                current_speaker = speaker
                current_text = [text] if text else []
            elif text:
                current_text.append(text)
            continue

        # Handle Speaker: text format
        colon_match = speaker_colon_pattern.match(line)
        if colon_match:
            speaker = colon_match.group(1).strip()
            text = colon_match.group(2).strip()

            if speaker != current_speaker:
                if current_speaker and current_text:
                    transcript_lines.append(f"{current_speaker}: {' '.join(current_text)}")
                current_speaker = speaker
                current_text = [text] if text else []
            elif text:
                current_text.append(text)
            continue

        # Regular text line (continuation of current speaker)
        # Remove any HTML-like tags
        clean_line = re.sub(r'<[^>]+>', '', line).strip()
        if clean_line:
            current_text.append(clean_line)

    # Don't forget the last speaker's text
    if current_speaker and current_text:
        transcript_lines.append(f"{current_speaker}: {' '.join(current_text)}")
    elif current_text:
        # No speaker identified, just join all text
        transcript_lines.append(' '.join(current_text))

    # Calculate duration
    duration_str = None
    if first_timestamp and last_timestamp:
        start_seconds = parse_vtt_timestamp(first_timestamp)
        end_seconds = parse_vtt_timestamp(last_timestamp)
        duration_seconds = end_seconds - start_seconds
        if duration_seconds > 0:
            duration_str = format_duration(duration_seconds)

    return '\n\n'.join(transcript_lines), duration_str


def is_vtt_content(text: str) -> bool:
    """
    Check if the given text appears to be VTT format.

    Args:
        text: Text to check

    Returns:
        True if text appears to be VTT format
    """
    text = text.strip()

    # Check for WEBVTT header
    if text.upper().startswith('WEBVTT'):
        return True

    # Check for timestamp patterns common in VTT
    timestamp_pattern = re.compile(r'\d{2}:\d{2}[:\.]?\d{0,2}\.?\d{0,3}\s*-->\s*\d{2}:\d{2}')
    if timestamp_pattern.search(text[:500]):  # Check first 500 chars
        return True

    return False


def preprocess_transcript(text: str) -> tuple[str, str | None]:
    """
    Preprocess transcript text, auto-detecting and parsing VTT if needed.

    Args:
        text: Raw input text (plain transcript or VTT)

    Returns:
        Tuple of (clean transcript text, duration string or None)
    """
    if is_vtt_content(text):
        return parse_vtt(text)
    return text.strip(), None


def format_summary_markdown(summary: dict) -> str:
    """
    Convert summary dict to formatted markdown string.
    Used for copy/download functionality.

    Args:
        summary: Parsed summary dictionary from LLM

    Returns:
        Formatted markdown string
    """
    lines = []

    # Title
    lines.append("# Meeting Summary\n")

    # TL;DR
    if summary.get("tldr"):
        lines.append("## TL;DR\n")
        lines.append(f"{summary['tldr']}\n")

    # Meeting Info
    lines.append("## Meeting Info\n")
    if summary.get("attendees"):
        lines.append(f"**Attendees:** {', '.join(summary['attendees'])}\n")
    if summary.get("duration_estimate"):
        lines.append(f"**Duration:** {summary['duration_estimate']}\n")

    # Key Topics
    if summary.get("key_topics"):
        lines.append("## Key Topics\n")
        for topic in summary["key_topics"]:
            lines.append(f"- {topic}")
        lines.append("")

    # Decisions
    if summary.get("decisions"):
        lines.append("## Key Decisions\n")
        for decision in summary["decisions"]:
            lines.append(f"- **{decision.get('decision', 'N/A')}**")
            if decision.get("context"):
                lines.append(f"  - Context: {decision['context']}")
        lines.append("")

    # Action Items
    lines.append("## Action Items\n")
    if summary.get("action_items"):
        lines.append("| Task | Owner | Deadline | Priority |")
        lines.append("|------|-------|----------|----------|")
        for item in summary["action_items"]:
            task = item.get("task", "N/A")
            owner = item.get("owner") or "Unassigned"
            deadline = item.get("deadline") or "Not set"
            priority = item.get("priority", "medium").capitalize()
            lines.append(f"| {task} | {owner} | {deadline} | {priority} |")
        lines.append("")
    else:
        lines.append("No action items identified.\n")

    # Open Questions
    if summary.get("open_questions"):
        lines.append("## Open Questions\n")
        for question in summary["open_questions"]:
            lines.append(f"- {question}")
        lines.append("")

    # Next Steps
    if summary.get("next_steps"):
        lines.append("## Next Steps\n")
        for i, step in enumerate(summary["next_steps"], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    return "\n".join(lines)


def validate_transcript(text: str) -> Tuple[bool, str]:
    """
    Basic validation of transcript input.

    Args:
        text: Raw transcript text

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message will be empty string
    """
    if not text or not text.strip():
        return False, "Please enter a meeting transcript."

    text = text.strip()

    if len(text) < 100:
        return False, "Transcript is too short. Please provide at least 100 characters for meaningful analysis."

    if len(text) > 50000:
        return False, f"Transcript is very long ({len(text):,} characters). Consider summarizing in sections or trimming to under 50,000 characters for best results."

    return True, ""


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate based on character count.
    Uses approximation of 4 characters per token.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // 4


def get_priority_badge(priority: str) -> str:
    """
    Get colored badge emoji for priority level.

    Args:
        priority: Priority string (high, medium, low)

    Returns:
        Emoji badge string
    """
    priority_badges = {
        "high": "🔴 High",
        "medium": "🟡 Medium",
        "low": "🟢 Low"
    }
    return priority_badges.get(priority.lower(), "🟡 Medium")


def get_sentiment_badge(sentiment: str) -> str:
    """
    Get colored badge emoji for sentiment.

    Args:
        sentiment: Sentiment string (positive, neutral, negative, mixed)

    Returns:
        Emoji badge string
    """
    sentiment_badges = {
        "positive": "😊 Positive",
        "neutral": "😐 Neutral",
        "negative": "😟 Negative",
        "mixed": "🔀 Mixed"
    }
    return sentiment_badges.get(sentiment.lower(), "😐 Neutral")


def format_enhanced_summary_markdown(summary: dict) -> str:
    """
    Convert enhanced summary dict to formatted markdown string.
    Handles both basic and enhanced summary formats.

    Args:
        summary: Parsed summary dictionary from LLM

    Returns:
        Formatted markdown string
    """
    lines = []

    # Title
    lines.append("# Meeting Summary\n")

    # TL;DR
    if summary.get("tldr"):
        lines.append("## TL;DR\n")
        lines.append(f"{summary['tldr']}\n")

    # Meeting Info
    lines.append("## Meeting Info\n")
    attendees = summary.get("attendees", [])
    if attendees:
        if isinstance(attendees[0], dict):
            names = [a.get("name", "") for a in attendees]
            lines.append(f"**Attendees:** {', '.join(names)}\n")
        else:
            lines.append(f"**Attendees:** {', '.join(attendees)}\n")
    if summary.get("duration_estimate"):
        lines.append(f"**Duration:** {summary['duration_estimate']}\n")

    # Sentiment (enhanced)
    sentiment = summary.get("sentiment", {})
    if sentiment:
        lines.append("## Meeting Sentiment\n")
        overall = sentiment.get("overall", "neutral")
        energy = sentiment.get("energy") or sentiment.get("energy_level", "")
        lines.append(f"**Overall Tone:** {overall.capitalize()}\n")
        if energy:
            lines.append(f"**Energy Level:** {energy.capitalize()}\n")
        if sentiment.get("dynamics"):
            lines.append(f"**Dynamics:** {sentiment['dynamics']}\n")

        agreements = sentiment.get("agreements", [])
        if agreements:
            lines.append("\n**Points of Agreement:**")
            for a in agreements:
                lines.append(f"- {a}")
            lines.append("")

        conflicts = sentiment.get("conflicts", [])
        if conflicts:
            lines.append("\n**Tensions/Disagreements:**")
            for c in conflicts:
                lines.append(f"- {c}")
            lines.append("")

    # Speaker Contributions (enhanced)
    if attendees and isinstance(attendees[0], dict) and any(a.get("contribution_summary") for a in attendees):
        lines.append("## Speaker Contributions\n")
        for attendee in attendees:
            name = attendee.get("name", "Unknown")
            role = attendee.get("role", "")
            contribution = attendee.get("contribution_summary", "")
            role_str = f" ({role})" if role else ""
            lines.append(f"### {name}{role_str}")
            if contribution:
                lines.append(f"{contribution}\n")

    # Key Topics
    topics = summary.get("key_topics", [])
    if topics:
        lines.append("## Key Topics\n")
        for topic in topics:
            if isinstance(topic, dict):
                lines.append(f"- **{topic.get('name', '')}**: {topic.get('outcome', '')}")
            else:
                lines.append(f"- {topic}")
        lines.append("")

    # Detailed Topics (enhanced)
    detailed_topics = summary.get("topics", [])
    if detailed_topics and isinstance(detailed_topics[0], dict):
        lines.append("## Topic Details\n")
        for topic in detailed_topics:
            name = topic.get("name", "")
            duration = topic.get("duration_estimate", "")
            outcome = topic.get("outcome", "")
            speakers = topic.get("speakers_involved", [])

            lines.append(f"### {name}")
            if duration:
                lines.append(f"**Duration:** {duration}")
            if speakers:
                lines.append(f"**Speakers:** {', '.join(speakers)}")
            if outcome:
                lines.append(f"**Outcome:** {outcome}")

            key_points = topic.get("key_points", [])
            if key_points:
                for point in key_points:
                    lines.append(f"- {point}")
            lines.append("")

    # Decisions
    if summary.get("decisions"):
        lines.append("## Key Decisions\n")
        for decision in summary["decisions"]:
            lines.append(f"- **{decision.get('decision', 'N/A')}**")
            if decision.get("context"):
                lines.append(f"  - Context: {decision['context']}")
        lines.append("")

    # Action Items
    lines.append("## Action Items\n")
    if summary.get("action_items"):
        lines.append("| Task | Owner | Deadline | Priority |")
        lines.append("|------|-------|----------|----------|")
        for item in summary["action_items"]:
            task = item.get("task", "N/A")
            owner = item.get("owner") or "Unassigned"
            deadline = item.get("deadline") or "Not set"
            priority = item.get("priority", "medium").capitalize()
            lines.append(f"| {task} | {owner} | {deadline} | {priority} |")
        lines.append("")
    else:
        lines.append("No action items identified.\n")

    # Open Questions
    if summary.get("open_questions"):
        lines.append("## Open Questions\n")
        for question in summary["open_questions"]:
            lines.append(f"- {question}")
        lines.append("")

    # Next Steps
    if summary.get("next_steps"):
        lines.append("## Next Steps\n")
        for i, step in enumerate(summary["next_steps"], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    # Notable Quotes (enhanced)
    quotes = summary.get("notable_quotes", [])
    if quotes:
        lines.append("## Notable Quotes\n")
        for quote in quotes[:5]:
            speaker = quote.get("speaker", "Unknown")
            text = quote.get("quote", "")
            significance = quote.get("significance") or quote.get("context", "")
            lines.append(f"> \"{text}\" - **{speaker}**")
            if significance:
                lines.append(f"> _{significance}_")
            lines.append("")

    return "\n".join(lines)
