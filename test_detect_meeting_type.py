"""Tests for meeting type detection module."""

import pytest
from detect_meeting_type import (
    MeetingType,
    DetectionResult,
    detect_meeting_type,
    extract_speakers,
    count_keyword_matches,
    detect_round_robin_pattern,
    detect_structural_patterns,
    needs_confirmation,
    format_confirmation_message,
    get_meeting_type_display_name,
    get_all_meeting_types,
)


class TestExtractSpeakers:
    """Tests for speaker extraction."""

    def test_extract_speakers_colon_format(self):
        transcript = """
        John: Hello everyone.
        Sarah: Hi John, ready to start?
        Mike: Yes, let's begin.
        """
        speakers = extract_speakers(transcript)
        assert len(speakers) == 3
        assert "John" in speakers
        assert "Sarah" in speakers
        assert "Mike" in speakers

    def test_extract_speakers_vtt_format(self):
        transcript = """
        <v John Smith>Hello everyone.
        <v Sarah Jones>Hi John, ready to start?
        """
        speakers = extract_speakers(transcript)
        assert "John Smith" in speakers
        assert "Sarah Jones" in speakers

    def test_extract_speakers_filters_non_names(self):
        transcript = """
        John: Hello.
        Note: This is a note.
        Action Item: Do something.
        Sarah: Goodbye.
        """
        speakers = extract_speakers(transcript)
        assert "John" in speakers
        assert "Sarah" in speakers
        assert "Note" not in speakers
        assert "Action Item" not in speakers


class TestCountKeywordMatches:
    """Tests for keyword matching."""

    def test_single_word_match(self):
        text = "We discussed the sprint backlog yesterday."
        keywords = ["sprint", "backlog", "velocity"]
        count, matches = count_keyword_matches(text, keywords)
        assert count == 2
        assert "sprint" in matches
        assert "backlog" in matches
        assert "velocity" not in matches

    def test_phrase_match(self):
        text = "The story points estimation went well."
        keywords = ["story points", "went well"]
        count, matches = count_keyword_matches(text, keywords)
        assert count == 2

    def test_case_insensitive(self):
        text = "SPRINT planning for BACKLOG items."
        keywords = ["sprint", "backlog"]
        count, matches = count_keyword_matches(text, keywords)
        assert count == 2


class TestRoundRobinDetection:
    """Tests for round-robin pattern detection."""

    def test_detects_round_robin(self):
        transcript = """
        John: Yesterday I worked on the API.
        Sarah: Yesterday I fixed bugs.
        Mike: Yesterday I did code review.
        John: Today I'll continue the API work.
        Sarah: Today I'll test the fixes.
        Mike: Today I'll review more PRs.
        """
        assert detect_round_robin_pattern(transcript) is True

    def test_no_round_robin_single_speaker(self):
        transcript = """
        John: I'm going to present the architecture.
        John: The system has three main components.
        John: Let me explain each one.
        """
        assert detect_round_robin_pattern(transcript) is False


class TestStructuralPatterns:
    """Tests for structural pattern detection."""

    def test_yesterday_today_blockers(self):
        transcript = """
        Yesterday I completed the feature.
        Today I'm working on tests.
        I have a blocker with the database.
        """
        patterns = detect_structural_patterns(transcript)
        assert patterns["yesterday_today_blockers"] is True

    def test_went_well_improve(self):
        transcript = """
        What went well: Team collaboration was great.
        What could improve: We need better documentation.
        """
        patterns = detect_structural_patterns(transcript)
        assert patterns["went_well_improve"] is True

    def test_story_estimation(self):
        transcript = """
        Let's estimate this user story.
        I think it's 5 points.
        """
        patterns = detect_structural_patterns(transcript)
        assert patterns["story_estimation"] is True

    def test_technical_deep_dive(self):
        transcript = """
        The architecture uses microservices.
        Each service has its own database.
        We need to consider API design and deployment.
        Performance and scalability are key.
        """
        patterns = detect_structural_patterns(transcript)
        assert patterns["technical_deep_dive"] is True


class TestDetectMeetingType:
    """Tests for main detection function."""

    def test_detect_standup(self):
        transcript = """
        John: Yesterday I completed the login feature. Today I'm working on the dashboard. No blockers.
        Sarah: Yesterday I fixed the API bug. Today I'll write tests. I'm blocked on database access.
        Mike: Yesterday I reviewed PRs. Today more code review. No blockers.
        """
        result = detect_meeting_type(transcript, title="Daily Standup")
        assert result.meeting_type == MeetingType.STANDUP
        assert result.confidence >= 0.5

    def test_detect_retrospective(self):
        transcript = """
        Let's start with what went well this sprint.
        Team: Collaboration was great, we shipped on time.
        Now what didn't go well?
        Team: Documentation could be better.
        What action items can we take to improve?
        """
        result = detect_meeting_type(transcript, title="Sprint 5 Retrospective")
        assert result.meeting_type == MeetingType.RETROSPECTIVE
        assert result.confidence >= 0.5

    def test_detect_sprint_planning(self):
        transcript = """
        Let's review the backlog for this sprint.
        This user story is about 5 story points.
        Our velocity from last sprint was 45 points.
        What's our capacity this sprint?
        We should commit to 40 points given PTO.
        """
        result = detect_meeting_type(transcript, title="Sprint Planning")
        assert result.meeting_type == MeetingType.SPRINT_PLANNING
        assert result.confidence >= 0.5

    def test_detect_one_on_one(self):
        transcript = """
        Manager: How are you doing this week?
        Employee: Pretty good, thanks for checking in.
        Manager: Let's talk about your career goals.
        Employee: I'd like to grow into a senior role.
        Manager: What feedback do you have for me?
        """
        result = detect_meeting_type(transcript, participant_count=2, title="1:1 Check-in")
        assert result.meeting_type == MeetingType.ONE_ON_ONE
        assert result.confidence >= 0.5

    def test_detect_architecture_review(self):
        transcript = """
        Today we'll review the proposed architecture.
        The system uses microservices with REST APIs.
        We need to consider scalability and performance.
        The database design follows this schema.
        Let's discuss the deployment infrastructure.
        """
        result = detect_meeting_type(transcript, title="Architecture Review")
        assert result.meeting_type == MeetingType.ARCHITECTURE
        assert result.confidence >= 0.5

    def test_detect_client_meeting(self):
        transcript = """
        Client: We need to discuss the project timeline.
        PM: Of course, let's review the deliverables.
        Client: The budget needs to stay within scope.
        PM: We'll ensure the requirements are met.
        """
        result = detect_meeting_type(transcript, title="Client Status Update")
        assert result.meeting_type == MeetingType.CLIENT
        assert result.confidence >= 0.5

    def test_detect_general_meeting(self):
        transcript = """
        Let's discuss various topics today.
        We have some updates to share.
        Any questions from the team?
        """
        result = detect_meeting_type(transcript)
        # Low keyword matches should default to general
        assert result.meeting_type == MeetingType.GENERAL

    def test_two_participants_boosts_one_on_one(self):
        transcript = """
        Person1: Let's chat about the project.
        Person2: Sure, sounds good.
        """
        result = detect_meeting_type(transcript, participant_count=2)
        # Two participants should significantly boost 1:1 score
        assert result.meeting_type in [MeetingType.ONE_ON_ONE, MeetingType.GENERAL]


class TestConfidenceAndConfirmation:
    """Tests for confidence and confirmation logic."""

    def test_needs_confirmation_low_confidence(self):
        result = DetectionResult(
            meeting_type=MeetingType.STANDUP,
            confidence=0.5,
            signals=[],
            keyword_matches={}
        )
        assert needs_confirmation(result) is True

    def test_no_confirmation_high_confidence(self):
        result = DetectionResult(
            meeting_type=MeetingType.STANDUP,
            confidence=0.8,
            signals=[],
            keyword_matches={}
        )
        assert needs_confirmation(result) is False

    def test_no_confirmation_general_meeting(self):
        result = DetectionResult(
            meeting_type=MeetingType.GENERAL,
            confidence=0.3,
            signals=[],
            keyword_matches={}
        )
        assert needs_confirmation(result) is False

    def test_format_confirmation_message(self):
        result = DetectionResult(
            meeting_type=MeetingType.STANDUP,
            confidence=0.65,
            signals=[],
            keyword_matches={}
        )
        message = format_confirmation_message(result)
        assert "Standup" in message
        assert "65%" in message
        assert "Available types" in message


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_meeting_type_display_name(self):
        assert get_meeting_type_display_name(MeetingType.SPRINT_PLANNING) == "Sprint Planning"
        assert get_meeting_type_display_name(MeetingType.ONE_ON_ONE) == "1-on-1"
        assert get_meeting_type_display_name(MeetingType.STANDUP) == "Daily Standup"

    def test_get_all_meeting_types(self):
        types = get_all_meeting_types()
        assert len(types) == 7  # All meeting types
        values = [t[0] for t in types]
        assert "sprint_planning" in values
        assert "standup" in values
        assert "general" in values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
