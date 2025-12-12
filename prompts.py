"""System prompts for meeting transcript analysis."""

from typing import Optional


# Meeting type-specific JSON templates
MEETING_TYPE_TEMPLATES = {
    "standup": '''{
  "tldr": "Brief summary of today's standup (under 50 words)",
  "attendees": ["Person 1", "Person 2"],
  "duration_estimate": "~15 minutes",
  "individual_updates": [
    {
      "person": "Name",
      "yesterday": "What they completed yesterday",
      "today": "What they plan to work on today",
      "blockers": ["Any blockers or impediments"]
    }
  ],
  "blockers": [
    {
      "description": "Blocker description",
      "owner": "Person affected",
      "needs_help_from": "Person or team who can help (or null)"
    }
  ],
  "team_announcements": ["Any team-wide announcements"],
  "follow_ups": ["Items needing follow-up after standup"]
}''',

    "sprint_planning": '''{
  "tldr": "Brief summary of sprint planning outcomes (under 50 words)",
  "attendees": ["Person 1", "Person 2"],
  "duration_estimate": "~2 hours",
  "sprint_goal": "The agreed sprint goal",
  "sprint_capacity": "Team capacity in story points or hours",
  "committed_stories": [
    {
      "title": "Story title",
      "points": "Story points",
      "assignee": "Primary owner (or null)",
      "acceptance_criteria": ["Key acceptance criteria"]
    }
  ],
  "stories_discussed_not_committed": [
    {
      "title": "Story title",
      "reason": "Why not committed this sprint"
    }
  ],
  "risks_identified": ["Potential risks to sprint success"],
  "dependencies": ["External dependencies identified"],
  "action_items": [
    {
      "task": "Task description",
      "owner": "Person responsible",
      "deadline": "Date if mentioned (or null)"
    }
  ]
}''',

    "retrospective": '''{
  "tldr": "Brief summary of retrospective outcomes (under 50 words)",
  "attendees": ["Person 1", "Person 2"],
  "duration_estimate": "~1 hour",
  "what_went_well": [
    {
      "item": "Positive item",
      "mentioned_by": ["People who mentioned it"],
      "votes": "Number of votes if applicable (or null)"
    }
  ],
  "what_didnt_go_well": [
    {
      "item": "Issue or problem",
      "mentioned_by": ["People who mentioned it"],
      "votes": "Number of votes if applicable (or null)"
    }
  ],
  "action_items": [
    {
      "improvement": "What will be improved",
      "owner": "Person responsible",
      "target_date": "When to complete (or null)",
      "priority": "high|medium|low"
    }
  ],
  "kudos": [
    {
      "from": "Person giving kudos",
      "to": "Person receiving",
      "reason": "Why"
    }
  ],
  "experiments_to_try": ["New things the team will try next sprint"],
  "parking_lot": ["Items to discuss later or in another forum"]
}''',

    "one_on_one": '''{
  "tldr": "Brief summary of 1-on-1 discussion (under 50 words)",
  "attendees": ["Manager", "Report"],
  "duration_estimate": "~30 minutes",
  "topics_discussed": [
    {
      "topic": "Topic name",
      "summary": "Brief discussion summary",
      "initiated_by": "Who brought it up"
    }
  ],
  "feedback_given": [
    {
      "from": "Person giving feedback",
      "to": "Person receiving",
      "type": "positive|constructive",
      "summary": "Feedback summary"
    }
  ],
  "career_development": {
    "goals_discussed": ["Career goals mentioned"],
    "growth_areas": ["Areas for development"],
    "progress_on_previous_goals": "Update on prior goals (or null)"
  },
  "concerns_raised": ["Any concerns or issues raised"],
  "support_needed": ["Support or resources requested"],
  "action_items": [
    {
      "task": "Task description",
      "owner": "Person responsible",
      "deadline": "Date if mentioned (or null)"
    }
  ],
  "next_meeting_topics": ["Topics to follow up on"]
}''',

    "client": '''{
  "tldr": "Brief summary of client meeting (under 50 words)",
  "attendees": [
    {
      "name": "Person name",
      "organization": "Company/team",
      "role": "Their role (or null)"
    }
  ],
  "duration_estimate": "~1 hour",
  "meeting_purpose": "Primary purpose of the meeting",
  "client_requirements": [
    {
      "requirement": "What the client needs",
      "priority": "high|medium|low",
      "clarifications_needed": "Any open questions"
    }
  ],
  "commitments_made": [
    {
      "commitment": "What was promised",
      "by_whom": "Who made the commitment",
      "deadline": "When (or null)"
    }
  ],
  "concerns_raised": [
    {
      "concern": "Client concern",
      "response": "How it was addressed",
      "resolved": true
    }
  ],
  "decisions": [
    {
      "decision": "What was decided",
      "stakeholders": ["People involved"]
    }
  ],
  "action_items": [
    {
      "task": "Task description",
      "owner": "Person responsible",
      "deadline": "Date if mentioned (or null)",
      "priority": "high|medium|low"
    }
  ],
  "next_steps": ["Agreed next steps"],
  "follow_up_meeting": "Date/time of next meeting (or null)"
}''',

    "architecture": '''{
  "tldr": "Brief summary of architecture discussion (under 50 words)",
  "attendees": ["Person 1", "Person 2"],
  "duration_estimate": "~1 hour",
  "systems_discussed": ["System or component names"],
  "technical_decisions": [
    {
      "decision": "What was decided",
      "alternatives_considered": ["Other options discussed"],
      "rationale": "Why this choice was made",
      "trade_offs": ["Trade-offs accepted"]
    }
  ],
  "architecture_changes": [
    {
      "component": "Affected component",
      "change": "What will change",
      "impact": "Expected impact",
      "migration_needed": true
    }
  ],
  "technical_debt_identified": [
    {
      "item": "Tech debt item",
      "severity": "high|medium|low",
      "proposed_solution": "How to address it (or null)"
    }
  ],
  "open_technical_questions": ["Unresolved technical questions"],
  "action_items": [
    {
      "task": "Task description",
      "owner": "Person responsible",
      "deadline": "Date if mentioned (or null)"
    }
  ],
  "diagrams_or_docs_needed": ["Documentation to be created"]
}''',

    "presentation": '''{
  "tldr": "Brief summary of presentation (under 50 words)",
  "presenter": "Main presenter name",
  "attendees": ["Audience members"],
  "duration_estimate": "~45 minutes",
  "purpose_of_presentation": "Why this presentation was given and its main objective",
  "executive_overview": "High-level summary of what was presented",
  "key_topics_presented": [
    {
      "topic": "Topic or section name",
      "summary": "What was covered",
      "key_takeaways": ["Main takeaway 1", "Main takeaway 2"]
    }
  ],
  "demonstrations_walkthroughs": [
    {
      "title": "What was demonstrated",
      "description": "Brief description of the demo",
      "outcome": "Result or audience reaction"
    }
  ],
  "questions_and_answers": [
    {
      "question": "Question from audience",
      "asked_by": "Person who asked (or null)",
      "answer": "Response given",
      "follow_up_needed": false
    }
  ],
  "decisions_or_agreements": [
    {
      "decision": "What was decided or agreed upon",
      "stakeholders": ["People involved"]
    }
  ],
  "action_items": [
    {
      "task": "Task description",
      "owner": "Person responsible",
      "deadline": "Date if mentioned (or null)"
    }
  ],
  "resources_shared": [
    {
      "resource": "Name or description of resource",
      "type": "link|document|slide deck|recording|other",
      "location": "URL or where to find it (or null)"
    }
  ]
}''',

    "general": '''{
  "tldr": "2-3 sentence executive summary (under 50 words)",
  "attendees": ["Person 1", "Person 2"],
  "duration_estimate": "~30 minutes",
  "key_topics": [
    "Topic 1 discussed",
    "Topic 2 discussed"
  ],
  "decisions": [
    {
      "decision": "What was decided",
      "context": "Why/how it was decided"
    }
  ],
  "action_items": [
    {
      "task": "Description of the task",
      "owner": "Person responsible (or null if unassigned)",
      "deadline": "Date if mentioned (or null)",
      "priority": "high|medium|low"
    }
  ],
  "open_questions": [
    "Question that wasn't resolved"
  ],
  "next_steps": [
    "Follow-up activity"
  ]
}'''
}


# Meeting type-specific guidelines
MEETING_TYPE_GUIDELINES = {
    "standup": """- Focus on extracting individual status updates (yesterday/today/blockers)
- Identify any blockers that need escalation
- Note team announcements or cross-cutting concerns
- Keep the summary very brief - standups are quick status syncs""",

    "sprint_planning": """- Extract the sprint goal clearly
- List all committed user stories with their point estimates
- Note any stories discussed but not committed and why
- Identify dependencies and risks to sprint success
- Capture capacity discussions""",

    "retrospective": """- Categorize items into what went well vs. what didn't
- Extract concrete action items for improvement
- Note any kudos or recognition given
- Capture experiments the team wants to try
- Record items put in the parking lot for later""",

    "one_on_one": """- Capture feedback given in both directions
- Note career development discussions and goals
- Identify concerns raised and support needed
- Keep personal/sensitive topics appropriately summarized
- Track action items for both participants""",

    "client": """- Clearly identify internal vs. client attendees
- Extract client requirements and their priorities
- Note all commitments made and by whom
- Capture client concerns and how they were addressed
- Track follow-up meeting schedules""",

    "architecture": """- Document technical decisions with rationale
- Note alternatives that were considered
- Identify trade-offs being accepted
- Capture technical debt items identified
- List any diagrams or documentation needed""",

    "presentation": """- Clearly state the purpose/objective of the presentation
- Provide an executive overview of what was presented
- Extract key topics with their main takeaways
- Document any demonstrations or walkthroughs shown
- Capture Q&A discussions with questions and answers
- Note any decisions or agreements reached
- Record resources shared (links, documents, slides, recordings)""",

    "general": """- Extract all attendees mentioned in the transcript
- Identify key topics and decisions
- Capture action items with owners and deadlines
- Note any unresolved questions
- List follow-up activities"""
}


def get_template_for_meeting_type(meeting_type: str) -> str:
    """Get the JSON template for a specific meeting type."""
    return MEETING_TYPE_TEMPLATES.get(meeting_type, MEETING_TYPE_TEMPLATES["general"])


def get_guidelines_for_meeting_type(meeting_type: str) -> str:
    """Get the analysis guidelines for a specific meeting type."""
    return MEETING_TYPE_GUIDELINES.get(meeting_type, MEETING_TYPE_GUIDELINES["general"])


def get_meeting_summary_prompt(meeting_type: Optional[str] = None) -> str:
    """
    Get the meeting summary system prompt for a specific meeting type.

    Args:
        meeting_type: The type of meeting (e.g., 'standup', 'retrospective').
                     If None, returns the general prompt.

    Returns:
        The system prompt string with the appropriate template.
    """
    if meeting_type is None:
        meeting_type = "general"

    template = get_template_for_meeting_type(meeting_type)
    guidelines = get_guidelines_for_meeting_type(meeting_type)
    meeting_type_display = meeting_type.replace('_', ' ').title()

    return f"""You are an expert meeting analyst. Your task is to analyze meeting transcripts and extract key information in a structured format.

This is a **{meeting_type_display}** meeting. Analyze the provided transcript and return ONLY valid JSON with the following structure:

{template}

Guidelines:
{guidelines}
- If no action items are found, return an empty array for "action_items"
- Infer priority based on urgency language:
  - "ASAP", "urgent", "critical", "immediately" = high
  - "soon", "this week", standard tasks = medium
  - "when possible", "eventually", "low priority" = low
- Extract deadlines in readable format (e.g., "December 15", "Next Monday", "End of week")
- If the owner of an action item is unclear, set owner to null
- Keep the TL;DR concise - under 50 words

CRITICAL: You MUST return a complete, valid JSON object. Do not truncate your response. If the content is long, prioritize completing the JSON structure over including every detail. Always ensure all strings are properly closed with quotes, all arrays with ], and all objects with {{}}.

Return ONLY the JSON object, no additional text or markdown formatting."""


def get_chunk_analysis_prompt(
    chunk_number: int,
    total_chunks: int,
    meeting_type: Optional[str] = None
) -> str:
    """
    Get the chunk analysis prompt for a specific meeting type.

    Args:
        chunk_number: Current chunk number
        total_chunks: Total number of chunks
        meeting_type: The type of meeting (e.g., 'standup', 'retrospective').
                     If None, uses the generic chunk analysis prompt.

    Returns:
        The chunk analysis prompt string.
    """
    if meeting_type is None:
        meeting_type = "general"

    guidelines = get_guidelines_for_meeting_type(meeting_type)
    meeting_type_display = meeting_type.replace('_', ' ').title()

    # Escape braces for .format() compatibility
    template = get_template_for_meeting_type(meeting_type).replace('{', '{{').replace('}', '}}')

    return f"""You are an expert meeting analyst. Analyze this segment of a meeting transcript and extract detailed information.

This is chunk {chunk_number} of {total_chunks} from a **{meeting_type_display}** meeting transcript.

Analyze and return ONLY valid JSON. The final merged summary will follow this structure, so extract relevant information for these fields:

{template}

Additionally, extract these chunk-specific details:
{{{{
  "chunk_summary": "2-3 sentence summary of this segment",
  "speakers": [
    {{{{
      "name": "Person's name",
      "role": "Role if mentioned (or null)",
      "key_contributions": ["Main point they made"]
    }}}}
  ],
  "key_quotes": [
    {{{{
      "speaker": "Name",
      "quote": "Important statement",
      "context": "Why this matters"
    }}}}
  ]
}}}}

Guidelines:
{guidelines}
- Extract ALL speakers mentioned, even if they speak briefly
- Extract notable quotes that capture key moments
- If this is a partial transcript, focus on what's visible in this segment

CRITICAL: You MUST return a complete, valid JSON object. Do not truncate your response.

Return ONLY the JSON object, no additional text."""


def get_merge_summaries_prompt(meeting_type: Optional[str] = None) -> str:
    """
    Get the merge summaries prompt for a specific meeting type.

    Args:
        meeting_type: The type of meeting (e.g., 'standup', 'retrospective').
                     If None, uses the generic merge prompt.

    Returns:
        The merge summaries prompt string.
    """
    if meeting_type is None:
        meeting_type = "general"

    template = get_template_for_meeting_type(meeting_type).replace('{', '{{').replace('}', '}}')
    guidelines = get_guidelines_for_meeting_type(meeting_type)
    meeting_type_display = meeting_type.replace('_', ' ').title()

    return f"""You are an expert meeting analyst. You will receive summaries from multiple chunks of a **{meeting_type_display}** meeting transcript. Your task is to merge them into one comprehensive final summary.

Combine the chunk summaries into a single cohesive meeting summary with this structure:

{template}

Guidelines:
{guidelines}

IMPORTANT Guidelines for merging:
- Deduplicate action items that appear in multiple chunks
- Merge speaker information across chunks (combine contributions)
- Create a cohesive narrative from topic fragments
- Prioritize the most important quotes (max 3-5)
- Ensure the TL;DR captures the full meeting, not just parts
- Remove any duplicate decisions or open questions

CRITICAL: You MUST return a complete, valid JSON object. Do not truncate your response. If the content is long, prioritize completing the JSON structure over including every detail. Always ensure all strings are properly closed with quotes, all arrays with ]], and all objects with }}}}.

Return ONLY the JSON object, no additional text."""


# Original prompt for single-chunk processing (backward compatibility)
MEETING_SUMMARY_SYSTEM_PROMPT = """You are an expert meeting analyst. Your task is to analyze meeting transcripts and extract key information in a structured format.

Analyze the provided meeting transcript and return ONLY valid JSON with the following structure:

{
  "tldr": "2-3 sentence executive summary (under 50 words)",
  "attendees": ["Person 1", "Person 2"],
  "duration_estimate": "~30 minutes",
  "key_topics": [
    "Topic 1 discussed",
    "Topic 2 discussed"
  ],
  "decisions": [
    {
      "decision": "What was decided",
      "context": "Why/how it was decided"
    }
  ],
  "action_items": [
    {
      "task": "Description of the task",
      "owner": "Person responsible (or null if unassigned)",
      "deadline": "Date if mentioned (or null)",
      "priority": "high|medium|low"
    }
  ],
  "open_questions": [
    "Question that wasn't resolved"
  ],
  "next_steps": [
    "Follow-up activity"
  ]
}

Guidelines:
- If no action items are found, return an empty array for "action_items"
- Infer priority based on urgency language:
  - "ASAP", "urgent", "critical", "immediately" = high
  - "soon", "this week", standard tasks = medium
  - "when possible", "eventually", "low priority" = low
- Extract deadlines in readable format (e.g., "December 15", "Next Monday", "End of week")
- If the owner of an action item is unclear, set owner to null
- Keep the TL;DR concise - under 50 words
- Extract all attendees mentioned in the transcript
- Estimate meeting duration based on content depth and number of topics
- Capture any unresolved questions or items needing follow-up

CRITICAL: You MUST return a complete, valid JSON object. Do not truncate your response. If the content is long, prioritize completing the JSON structure over including every detail. Always ensure all strings are properly closed with quotes, all arrays with ], and all objects with }.

Return ONLY the JSON object, no additional text or markdown formatting."""


# Enhanced prompt for chunk analysis with speaker attribution and topics
CHUNK_ANALYSIS_PROMPT = """You are an expert meeting analyst. Analyze this segment of a meeting transcript and extract detailed information.

This is chunk {chunk_number} of {total_chunks} from a longer meeting transcript.

Analyze and return ONLY valid JSON with the following structure:

{{
  "chunk_summary": "2-3 sentence summary of this segment",
  "speakers": [
    {{
      "name": "Person's name",
      "role": "Role if mentioned (or null)",
      "key_contributions": ["Main point they made", "Another contribution"],
      "speaking_time_estimate": "percentage or relative amount"
    }}
  ],
  "topics": [
    {{
      "name": "Topic discussed",
      "description": "Brief description of discussion",
      "speakers_involved": ["Name1", "Name2"],
      "outcome": "What was decided or concluded (or 'ongoing')"
    }}
  ],
  "action_items": [
    {{
      "task": "Description of the task",
      "owner": "Person responsible (or null)",
      "deadline": "Date if mentioned (or null)",
      "priority": "high|medium|low",
      "context": "Why this action was assigned"
    }}
  ],
  "decisions": [
    {{
      "decision": "What was decided",
      "context": "Why/how it was decided",
      "stakeholders": ["People involved in decision"]
    }}
  ],
  "key_quotes": [
    {{
      "speaker": "Name",
      "quote": "Important or notable statement",
      "context": "Why this quote matters"
    }}
  ],
  "open_questions": ["Question that wasn't resolved"],
  "follow_ups_mentioned": ["Any follow-up items or meetings mentioned"]
}}

Guidelines:
- Extract ALL speakers mentioned, even if they speak briefly
- Extract notable quotes that capture key moments
- If this is a partial transcript, focus on what's visible in this segment

CRITICAL: You MUST return a complete, valid JSON object. Do not truncate your response. If the content is long, prioritize completing the JSON structure over including every detail. Always ensure all strings are properly closed with quotes, all arrays with ], and all objects with }}.

Return ONLY the JSON object, no additional text."""


# Prompt for merging multiple chunk summaries into final summary
MERGE_SUMMARIES_PROMPT = """You are an expert meeting analyst. You will receive summaries from multiple chunks of a single meeting transcript. Your task is to merge them into one comprehensive final summary.

Combine the chunk summaries into a single cohesive meeting summary with this structure:

{{
  "tldr": "2-3 sentence executive summary of the ENTIRE meeting (under 50 words)",
  "attendees": [
    {{
      "name": "Person's name",
      "role": "Their role",
      "contribution_summary": "Brief summary of their main contributions across the meeting"
    }}
  ],
  "duration_estimate": "Estimated total meeting duration",
  "topics": [
    {{
      "name": "Topic name",
      "duration_estimate": "How long spent on this topic",
      "speakers_involved": ["Name1", "Name2"],
      "outcome": "What was concluded or decided",
      "key_points": ["Main point 1", "Main point 2"]
    }}
  ],
  "action_items": [
    {{
      "task": "Description of the task",
      "owner": "Person responsible (or null)",
      "deadline": "Date if mentioned (or null)",
      "priority": "high|medium|low"
    }}
  ],
  "decisions": [
    {{
      "decision": "What was decided",
      "context": "Why/how it was decided"
    }}
  ],
  "key_topics": ["Topic 1", "Topic 2"],
  "open_questions": ["Unresolved question"],
  "next_steps": ["Follow-up activity"],
  "notable_quotes": [
    {{
      "speaker": "Name",
      "quote": "The quote",
      "significance": "Why it matters"
    }}
  ]
}}

IMPORTANT Guidelines for merging:
- Deduplicate action items that appear in multiple chunks
- Merge speaker information across chunks (combine contributions)
- Create a cohesive narrative from topic fragments
- Prioritize the most important quotes (max 3-5)
- Ensure the TL;DR captures the full meeting, not just parts
- Remove any duplicate decisions or open questions

CRITICAL: You MUST return a complete, valid JSON object. Do not truncate your response. If the content is long, prioritize completing the JSON structure over including every detail. Always ensure all strings are properly closed with quotes, all arrays with ], and all objects with }}.

Return ONLY the JSON object, no additional text."""
