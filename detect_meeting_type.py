"""Meeting type detection module.

Automatically detects meeting types based on keywords, duration,
participant count, and structural patterns in the transcript.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MeetingType(Enum):
    """Supported meeting types with specialized templates."""
    SPRINT_PLANNING = "sprint_planning"
    STANDUP = "standup"
    RETROSPECTIVE = "retrospective"
    ONE_ON_ONE = "one_on_one"
    CLIENT = "client"
    ARCHITECTURE = "architecture"
    PRESENTATION = "presentation"
    GENERAL = "general"


@dataclass
class DetectionResult:
    """Result of meeting type detection."""
    meeting_type: MeetingType
    confidence: float  # 0.0 to 1.0
    signals: list[str]  # Reasons for the detection
    keyword_matches: dict[str, list[str]]  # Keywords found per category


# Keyword patterns for each meeting type
MEETING_TYPE_KEYWORDS: dict[str, list[str]] = {
    "sprint_planning": [
        "sprint", "story points", "backlog", "velocity", "commitment",
        "sprint goal", "user stories", "estimation", "capacity", "planning poker",
        "story", "points", "refinement", "grooming", "sprint planning"
    ],
    "standup": [
        "yesterday", "today", "tomorrow", "blockers", "impediments",
        "status update", "daily", "scrum", "working on", "plan to",
        "blocked", "standup", "stand-up", "daily standup"
    ],
    "retrospective": [
        "went well", "didn't work", "improve", "action items", "lessons learned",
        "retro", "iteration", "reflection", "what worked", "continue doing",
        "stop doing", "start doing", "retrospective", "could be better",
        "kudos", "shoutout"
    ],
    "one_on_one": [
        "career", "feedback", "goals", "development", "concerns", "support",
        "growth", "performance", "1:1", "one-on-one", "coaching", "mentoring",
        "promotion", "raise", "personal", "how are you", "wellbeing",
        "work-life", "check-in"
    ],
    "client": [
        "client", "stakeholder", "proposal", "requirements", "deliverables",
        "timeline", "contract", "engagement", "scope", "budget", "vendor",
        "customer", "invoice", "milestone", "demo", "presentation", "showcase"
    ],
    "architecture": [
        "architecture", "design", "technical", "scalability", "patterns",
        "infrastructure", "system", "component", "integration", "microservices",
        "deployment", "database", "api", "schema", "diagram", "tech debt",
        "refactor", "performance", "load", "latency", "caching"
    ],
    "presentation": [
        "presentation", "demo", "walkthrough", "showcase", "slides", "deck",
        "overview", "introduce", "presenting", "show you", "let me show",
        "questions at the end", "q&a", "any questions", "screen share",
        "powerpoint", "keynote", "demonstrate"
    ]
}

# Typical duration ranges in minutes for each meeting type
MEETING_DURATION_RANGES: dict[str, tuple[int, int]] = {
    "standup": (5, 20),
    "one_on_one": (20, 60),
    "retrospective": (45, 120),
    "sprint_planning": (60, 240),
    "architecture": (30, 120),
    "client": (30, 90),
    "presentation": (30, 90),
}


def extract_speakers(transcript: str) -> list[str]:
    """
    Extract unique speaker names from transcript.

    Args:
        transcript: Meeting transcript text

    Returns:
        List of unique speaker names
    """
    speakers = set()

    # Pattern 1: "Name:" at start of line
    pattern1 = re.compile(r'^([A-Z][a-zA-Z\s\.\-]+):', re.MULTILINE)
    for match in pattern1.finditer(transcript):
        name = match.group(1).strip()
        # Filter out common non-name patterns
        if len(name) < 50 and not any(word in name.lower() for word in
            ['note', 'action', 'decision', 'summary', 'topic', 'agenda']):
            speakers.add(name)

    # Pattern 2: "<v Name>" VTT format
    pattern2 = re.compile(r'<v\s+([^>]+)>')
    for match in pattern2.finditer(transcript):
        speakers.add(match.group(1).strip())

    return list(speakers)


def count_keyword_matches(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    """
    Count keyword matches in text.

    Args:
        text: Text to search
        keywords: List of keywords to find

    Returns:
        Tuple of (match_count, list_of_matched_keywords)
    """
    text_lower = text.lower()
    matches = []

    for keyword in keywords:
        # Use word boundaries for single words, simple search for phrases
        if ' ' in keyword:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        else:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matches.append(keyword)

    return len(matches), matches


def detect_round_robin_pattern(transcript: str) -> bool:
    """
    Detect if transcript follows a round-robin speaking pattern.

    This is characteristic of standups where each person speaks in turn
    with relatively equal, short segments.

    Args:
        transcript: Meeting transcript text

    Returns:
        True if round-robin pattern detected
    """
    speakers = extract_speakers(transcript)
    if len(speakers) < 2:
        return False

    # Split transcript by speaker turns
    pattern = re.compile(r'^([A-Z][a-zA-Z\s\.\-]+):', re.MULTILINE)
    turns = pattern.split(transcript)

    # Filter and count speaker appearances
    speaker_turns = {}
    for i, turn in enumerate(turns):
        if turn.strip() in speakers:
            speaker_turns[turn.strip()] = speaker_turns.get(turn.strip(), 0) + 1

    if not speaker_turns:
        return False

    # Check if speakers have roughly equal number of turns (within 50%)
    turn_counts = list(speaker_turns.values())
    avg_turns = sum(turn_counts) / len(turn_counts)

    if avg_turns < 1:
        return False

    # All speakers should have at least 1 turn and be within 50% of average
    variance_ok = all(0.5 * avg_turns <= count <= 1.5 * avg_turns
                      for count in turn_counts)

    return variance_ok and len(turn_counts) >= 2


def detect_structural_patterns(transcript: str) -> dict[str, bool]:
    """
    Detect structural patterns in the transcript.

    Args:
        transcript: Meeting transcript text

    Returns:
        Dict of pattern names to boolean indicating if detected
    """
    patterns = {
        "round_robin": detect_round_robin_pattern(transcript),
        "yesterday_today_blockers": False,
        "went_well_improve": False,
        "story_estimation": False,
        "technical_deep_dive": False,
        "single_dominant_speaker": False,
    }

    text_lower = transcript.lower()

    # Yesterday/Today/Blockers structure (standup)
    has_yesterday = any(word in text_lower for word in ['yesterday', 'last day', 'previously'])
    has_today = any(word in text_lower for word in ['today', 'this day', 'planning to'])
    has_blockers = any(word in text_lower for word in ['blocker', 'blocked', 'impediment', 'stuck'])
    patterns["yesterday_today_blockers"] = has_yesterday and has_today

    # Went well / Improve structure (retrospective)
    has_went_well = any(phrase in text_lower for phrase in
        ['went well', 'worked well', 'good job', 'proud of', 'celebrate'])
    has_improve = any(phrase in text_lower for phrase in
        ['improve', 'better', 'didn\'t work', 'could have', 'next time'])
    patterns["went_well_improve"] = has_went_well and has_improve

    # Story estimation patterns (sprint planning)
    has_story = 'story' in text_lower or 'user story' in text_lower
    has_points = any(word in text_lower for word in ['points', 'estimate', 'sizing', 'fibonacci'])
    patterns["story_estimation"] = has_story and has_points

    # Technical deep dive (architecture)
    tech_terms = ['architecture', 'database', 'api', 'service', 'component',
                  'infrastructure', 'deployment', 'scalability', 'performance']
    tech_count = sum(1 for term in tech_terms if term in text_lower)
    patterns["technical_deep_dive"] = tech_count >= 4

    # Single dominant speaker pattern (presentation)
    # Check if one speaker has significantly more speaking time than others
    speakers = extract_speakers(transcript)
    if len(speakers) >= 2:
        # Count words per speaker (rough approximation of speaking time)
        speaker_pattern = re.compile(r'^([A-Z][a-zA-Z\s\.\-]+):', re.MULTILINE)
        parts = speaker_pattern.split(transcript)
        speaker_words: dict[str, int] = {}
        current_speaker = None
        for part in parts:
            if part.strip() in speakers:
                current_speaker = part.strip()
            elif current_speaker:
                speaker_words[current_speaker] = speaker_words.get(current_speaker, 0) + len(part.split())

        if speaker_words:
            total_words = sum(speaker_words.values())
            if total_words > 0:
                max_speaker_words = max(speaker_words.values())
                # If one speaker has 70%+ of the words, it's likely a presentation
                patterns["single_dominant_speaker"] = (max_speaker_words / total_words) >= 0.7

    return patterns


def estimate_duration_minutes(transcript: str, explicit_duration: Optional[str] = None) -> Optional[int]:
    """
    Estimate meeting duration in minutes.

    Args:
        transcript: Meeting transcript text
        explicit_duration: Duration string if provided (e.g., "1 hour 30 minutes")

    Returns:
        Estimated duration in minutes, or None if unable to estimate
    """
    if explicit_duration:
        # Parse explicit duration string
        minutes = 0
        hour_match = re.search(r'(\d+)\s*hour', explicit_duration.lower())
        min_match = re.search(r'(\d+)\s*min', explicit_duration.lower())

        if hour_match:
            minutes += int(hour_match.group(1)) * 60
        if min_match:
            minutes += int(min_match.group(1))

        if minutes > 0:
            return minutes

    # Estimate based on transcript length (rough heuristic)
    # Average speaking rate ~150 words/minute
    # Average transcript has ~80% speaking time capture
    word_count = len(transcript.split())
    estimated_minutes = word_count / 120  # Conservative estimate

    return int(estimated_minutes) if estimated_minutes > 0 else None


def calculate_type_scores(
    transcript: str,
    participant_count: int,
    duration_minutes: Optional[int],
    title: Optional[str] = None
) -> dict[str, float]:
    """
    Calculate confidence scores for each meeting type.

    Args:
        transcript: Meeting transcript text
        participant_count: Number of participants
        duration_minutes: Meeting duration in minutes
        title: Optional meeting title

    Returns:
        Dict mapping meeting type to confidence score (0.0-1.0)
    """
    scores: dict[str, float] = {mt.value: 0.0 for mt in MeetingType}
    keyword_results: dict[str, tuple[int, list[str]]] = {}

    # Combine transcript and title for keyword search
    search_text = transcript
    if title:
        search_text = title + "\n" + transcript

    # Score based on keyword matches
    for meeting_type, keywords in MEETING_TYPE_KEYWORDS.items():
        count, matches = count_keyword_matches(search_text, keywords)
        keyword_results[meeting_type] = (count, matches)

        # Normalize keyword score (0-0.4 based on matches)
        # 3+ matches = full 0.4 score
        keyword_score = min(count / 3, 1.0) * 0.4
        scores[meeting_type] = keyword_score

    # Structural pattern bonuses
    patterns = detect_structural_patterns(transcript)

    if patterns["round_robin"] and patterns["yesterday_today_blockers"]:
        scores["standup"] += 0.3
    elif patterns["round_robin"]:
        scores["standup"] += 0.15

    if patterns["went_well_improve"]:
        scores["retrospective"] += 0.25

    if patterns["story_estimation"]:
        scores["sprint_planning"] += 0.25

    if patterns["technical_deep_dive"]:
        scores["architecture"] += 0.2

    if patterns["single_dominant_speaker"]:
        scores["presentation"] += 0.25

    # Participant count scoring
    if participant_count == 2:
        scores["one_on_one"] += 0.35
    elif participant_count <= 4:
        scores["one_on_one"] += 0.1
    elif participant_count > 8:
        scores["one_on_one"] -= 0.2  # Very unlikely to be 1:1

    # Duration scoring
    if duration_minutes:
        for meeting_type, (min_dur, max_dur) in MEETING_DURATION_RANGES.items():
            if min_dur <= duration_minutes <= max_dur:
                scores[meeting_type] += 0.15
            elif duration_minutes < min_dur * 0.5 or duration_minutes > max_dur * 2:
                scores[meeting_type] -= 0.1

    # Title keyword bonus (title is very strong signal)
    if title:
        title_lower = title.lower()

        if any(word in title_lower for word in ['standup', 'stand-up', 'daily', 'scrum']):
            scores["standup"] += 0.3
        if any(word in title_lower for word in ['retro', 'retrospective']):
            scores["retrospective"] += 0.3
        if any(word in title_lower for word in ['planning', 'sprint', 'grooming', 'refinement']):
            scores["sprint_planning"] += 0.3
        if any(word in title_lower for word in ['1:1', '1-1', 'one-on-one', '1 on 1']):
            scores["one_on_one"] += 0.3
        if any(word in title_lower for word in ['client', 'customer', 'stakeholder']):
            scores["client"] += 0.3
        if any(word in title_lower for word in ['architecture', 'design', 'technical', 'tech review']):
            scores["architecture"] += 0.3
        if any(word in title_lower for word in ['presentation', 'demo', 'showcase', 'walkthrough', 'overview']):
            scores["presentation"] += 0.3

    # Normalize scores to 0-1 range
    for mt in scores:
        scores[mt] = max(0.0, min(1.0, scores[mt]))

    return scores


def detect_meeting_type(
    transcript: str,
    participant_count: Optional[int] = None,
    duration_minutes: Optional[int] = None,
    duration_string: Optional[str] = None,
    title: Optional[str] = None
) -> DetectionResult:
    """
    Detect the meeting type from transcript and metadata.

    Args:
        transcript: Meeting transcript text
        participant_count: Number of participants (auto-detected if None)
        duration_minutes: Meeting duration in minutes
        duration_string: Duration as string (e.g., "1 hour 30 minutes")
        title: Optional meeting title

    Returns:
        DetectionResult with meeting type, confidence, and signals
    """
    # Auto-detect participant count if not provided
    if participant_count is None:
        speakers = extract_speakers(transcript)
        participant_count = len(speakers) if speakers else 0

    # Parse duration if string provided
    if duration_minutes is None and duration_string:
        duration_minutes = estimate_duration_minutes(transcript, duration_string)
    elif duration_minutes is None:
        duration_minutes = estimate_duration_minutes(transcript)

    # Calculate scores for each type
    scores = calculate_type_scores(
        transcript=transcript,
        participant_count=participant_count,
        duration_minutes=duration_minutes,
        title=title
    )

    # Get keyword matches for result
    keyword_matches: dict[str, list[str]] = {}
    for meeting_type, keywords in MEETING_TYPE_KEYWORDS.items():
        search_text = (title + "\n" if title else "") + transcript
        _, matches = count_keyword_matches(search_text, keywords)
        if matches:
            keyword_matches[meeting_type] = matches

    # Find best match
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # Build signals list
    signals = []

    if participant_count:
        signals.append(f"Detected {participant_count} participants")
    if duration_minutes:
        signals.append(f"Estimated duration: {duration_minutes} minutes")
    if title:
        signals.append(f"Meeting title: {title}")

    # Add keyword signals
    if best_type in keyword_matches:
        top_keywords = keyword_matches[best_type][:5]
        signals.append(f"Keywords found: {', '.join(top_keywords)}")

    # Add structural signals
    patterns = detect_structural_patterns(transcript)
    if patterns["round_robin"]:
        signals.append("Round-robin speaking pattern detected")
    if patterns["yesterday_today_blockers"]:
        signals.append("Yesterday/Today/Blockers structure detected")
    if patterns["went_well_improve"]:
        signals.append("Retrospective structure detected")
    if patterns["story_estimation"]:
        signals.append("Story estimation discussion detected")
    if patterns["technical_deep_dive"]:
        signals.append("Technical deep-dive content detected")
    if patterns["single_dominant_speaker"]:
        signals.append("Single dominant speaker pattern detected")

    # If confidence is too low, default to general
    if best_score < 0.3:
        return DetectionResult(
            meeting_type=MeetingType.GENERAL,
            confidence=1.0 - best_score,  # Confidence in "general" classification
            signals=["No strong signals for specific meeting type"] + signals,
            keyword_matches=keyword_matches
        )

    return DetectionResult(
        meeting_type=MeetingType(best_type),
        confidence=best_score,
        signals=signals,
        keyword_matches=keyword_matches
    )


def needs_confirmation(result: DetectionResult) -> bool:
    """
    Check if detection result needs user confirmation.

    Args:
        result: DetectionResult from detect_meeting_type

    Returns:
        True if confidence < 70% and should ask user to confirm
    """
    return result.confidence < 0.7 and result.meeting_type != MeetingType.GENERAL


def format_confirmation_message(result: DetectionResult) -> str:
    """
    Format a message asking the user to confirm the detected meeting type.

    Args:
        result: DetectionResult from detect_meeting_type

    Returns:
        Formatted confirmation message
    """
    confidence_pct = int(result.confidence * 100)
    type_name = result.meeting_type.value.replace('_', ' ').title()

    message = (
        f"Based on my analysis, this appears to be a **{type_name}** meeting "
        f"(confidence: {confidence_pct}%). Is this correct?\n\n"
        f"Available types: Sprint Planning, Standup, Retrospective, "
        f"1-on-1, Client Meeting, Architecture Review, Presentation, General."
    )

    return message


def get_meeting_type_display_name(meeting_type: MeetingType) -> str:
    """
    Get human-readable display name for meeting type.

    Args:
        meeting_type: MeetingType enum value

    Returns:
        Display name string
    """
    display_names = {
        MeetingType.SPRINT_PLANNING: "Sprint Planning",
        MeetingType.STANDUP: "Daily Standup",
        MeetingType.RETROSPECTIVE: "Retrospective",
        MeetingType.ONE_ON_ONE: "1-on-1",
        MeetingType.CLIENT: "Client Meeting",
        MeetingType.ARCHITECTURE: "Architecture Review",
        MeetingType.PRESENTATION: "Presentation",
        MeetingType.GENERAL: "General Meeting",
    }
    return display_names.get(meeting_type, "General Meeting")


def get_all_meeting_types() -> list[tuple[str, str]]:
    """
    Get all meeting types with their display names.

    Returns:
        List of (enum_value, display_name) tuples
    """
    return [
        (mt.value, get_meeting_type_display_name(mt))
        for mt in MeetingType
    ]
