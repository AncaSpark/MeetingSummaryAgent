"""Meeting Summary Agent - Streamlit Application."""

import os
import streamlit as st
from dotenv import load_dotenv

from langbase_client import LangbaseClient
from pipeline import MeetingPipeline
from utils import (
    format_summary_markdown,
    format_enhanced_summary_markdown,
    validate_transcript,
    estimate_tokens,
    get_priority_badge,
    preprocess_transcript,
    is_vtt_content
)
from detect_meeting_type import (
    detect_meeting_type,
    MeetingType,
    get_meeting_type_display_name,
    get_all_meeting_types,
    needs_confirmation
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Meeting Summary Agent",
    page_icon="📋",
    layout="wide"
)

# Initialize session state
if "summary" not in st.session_state:
    st.session_state.summary = None
if "error" not in st.session_state:
    st.session_state.error = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "processing_info" not in st.session_state:
    st.session_state.processing_info = None  # Stores chunk count, etc.
if "detected_meeting_type" not in st.session_state:
    st.session_state.detected_meeting_type = None
if "selected_meeting_type" not in st.session_state:
    st.session_state.selected_meeting_type = None
if "last_transcript_hash" not in st.session_state:
    st.session_state.last_transcript_hash = None


def get_api_key() -> str:
    """Get API key from Streamlit secrets or environment variable."""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["LANGBASE_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

    # Fall back to environment variable (for local development)
    return os.getenv("LANGBASE_API_KEY", "")


def display_common_header(summary: dict):
    """Display common header elements for all meeting types."""
    # TL;DR Section
    st.info(f"**TL;DR:** {summary.get('tldr', 'No summary available.')}")

    # Meeting Info
    col1, col2, col3 = st.columns(3)
    with col1:
        attendees = summary.get("attendees", [])
        if attendees:
            # Handle both simple list and enhanced format
            if isinstance(attendees[0], dict):
                names = [a.get("name", "") for a in attendees]
                st.markdown(f"**Attendees:** {', '.join(names)}")
            else:
                st.markdown(f"**Attendees:** {', '.join(attendees)}")
    with col2:
        duration = summary.get("duration_estimate", "Unknown")
        st.markdown(f"**Estimated Duration:** {duration}")
    with col3:
        meeting_type_display = summary.get("meeting_type_display")
        if meeting_type_display:
            st.markdown(f"**Meeting Type:** {meeting_type_display}")

    st.divider()


def display_action_items(action_items: list, show_context: bool = False):
    """Display action items in a table format."""
    st.subheader("Action Items")
    if action_items:
        # Create table header
        if show_context:
            cols = st.columns([2.5, 1.5, 1.5, 1, 2])
            cols[0].markdown("**Task**")
            cols[1].markdown("**Owner**")
            cols[2].markdown("**Deadline**")
            cols[3].markdown("**Priority**")
            cols[4].markdown("**Context**")
        else:
            cols = st.columns([3, 2, 2, 1.5])
            cols[0].markdown("**Task**")
            cols[1].markdown("**Owner**")
            cols[2].markdown("**Deadline**")
            cols[3].markdown("**Priority**")

        # Table rows
        for item in action_items:
            if show_context:
                cols = st.columns([2.5, 1.5, 1.5, 1, 2])
                cols[0].write(item.get("task") or item.get("improvement", "N/A"))
                cols[1].write(item.get("owner") or "Unassigned")
                cols[2].write(item.get("deadline") or item.get("target_date") or "Not set")
                cols[3].write(get_priority_badge(item.get("priority", "medium")))
                cols[4].write(item.get("context", ""))
            else:
                cols = st.columns([3, 2, 2, 1.5])
                cols[0].write(item.get("task") or item.get("improvement", "N/A"))
                cols[1].write(item.get("owner") or "Unassigned")
                cols[2].write(item.get("deadline") or item.get("target_date") or "Not set")
                cols[3].write(get_priority_badge(item.get("priority", "medium")))
    else:
        st.write("No action items found.")


def display_export_options(summary: dict):
    """Display export options."""
    st.subheader("Export")
    markdown_content = format_enhanced_summary_markdown(summary)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download as Markdown",
            data=markdown_content,
            file_name="meeting_summary.md",
            mime="text/markdown"
        )
    with col2:
        with st.expander("📋 Copy to Clipboard"):
            st.text_area(
                "Select all and copy (Ctrl+A, Ctrl+C):",
                value=markdown_content,
                height=200,
                label_visibility="collapsed"
            )


def display_standup_summary(summary: dict):
    """Display standup meeting summary."""
    display_common_header(summary)

    # Individual Updates
    individual_updates = summary.get("individual_updates", [])
    if individual_updates:
        st.subheader("Individual Updates")
        for update in individual_updates:
            person = update.get("person", "Unknown")
            with st.expander(f"🧑 {person}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Yesterday:**")
                    st.write(update.get("yesterday", "Not specified"))
                with col2:
                    st.markdown("**Today:**")
                    st.write(update.get("today", "Not specified"))

                blockers = update.get("blockers", [])
                if blockers and blockers[0]:  # Check for non-empty blockers
                    st.markdown("**Blockers:**")
                    for blocker in blockers:
                        st.warning(f"🚧 {blocker}")
        st.divider()

    # Team-wide Blockers
    blockers = summary.get("blockers", [])
    if blockers:
        st.subheader("🚧 Blockers Needing Attention")
        for blocker in blockers:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.warning(f"**{blocker.get('description', 'N/A')}**")
                st.caption(f"Affects: {blocker.get('owner', 'Unknown')}")
            with col2:
                needs_help = blocker.get("needs_help_from")
                if needs_help:
                    st.info(f"Needs: {needs_help}")
        st.divider()

    # Team Announcements
    announcements = summary.get("team_announcements", [])
    if announcements:
        st.subheader("📢 Team Announcements")
        for announcement in announcements:
            st.info(announcement)
        st.divider()

    # Follow-ups
    follow_ups = summary.get("follow_ups", [])
    if follow_ups:
        st.subheader("Follow-ups")
        for i, item in enumerate(follow_ups, 1):
            st.markdown(f"{i}. {item}")

    st.divider()
    display_export_options(summary)


def display_sprint_planning_summary(summary: dict):
    """Display sprint planning meeting summary."""
    display_common_header(summary)

    # Sprint Goal and Capacity
    col1, col2 = st.columns(2)
    with col1:
        sprint_goal = summary.get("sprint_goal", "Not defined")
        st.success(f"**🎯 Sprint Goal:** {sprint_goal}")
    with col2:
        capacity = summary.get("sprint_capacity", "Not specified")
        st.info(f"**📊 Team Capacity:** {capacity}")

    st.divider()

    # Committed Stories
    committed = summary.get("committed_stories", [])
    if committed:
        st.subheader("✅ Committed Stories")
        for story in committed:
            with st.expander(f"📋 {story.get('title', 'Untitled')} ({story.get('points', '?')} pts)"):
                assignee = story.get("assignee")
                if assignee:
                    st.markdown(f"**Assignee:** {assignee}")
                criteria = story.get("acceptance_criteria", [])
                if criteria:
                    st.markdown("**Acceptance Criteria:**")
                    for c in criteria:
                        st.markdown(f"- {c}")
        st.divider()

    # Stories Not Committed
    not_committed = summary.get("stories_discussed_not_committed", [])
    if not_committed:
        st.subheader("⏸️ Discussed but Not Committed")
        for story in not_committed:
            st.markdown(f"- **{story.get('title', 'Untitled')}**: {story.get('reason', 'No reason given')}")
        st.divider()

    # Risks and Dependencies
    col1, col2 = st.columns(2)
    with col1:
        risks = summary.get("risks_identified", [])
        if risks:
            st.subheader("⚠️ Risks")
            for risk in risks:
                st.warning(risk)
    with col2:
        dependencies = summary.get("dependencies", [])
        if dependencies:
            st.subheader("🔗 Dependencies")
            for dep in dependencies:
                st.info(dep)

    st.divider()
    display_action_items(summary.get("action_items", []))
    st.divider()
    display_export_options(summary)


def display_retrospective_summary(summary: dict):
    """Display retrospective meeting summary."""
    display_common_header(summary)

    # What went well / What didn't
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ What Went Well")
        went_well = summary.get("what_went_well", [])
        if went_well:
            for item in went_well:
                votes = item.get("votes")
                vote_str = f" ({votes} votes)" if votes else ""
                st.success(f"**{item.get('item', 'N/A')}**{vote_str}")
                mentioned_by = item.get("mentioned_by", [])
                if mentioned_by:
                    st.caption(f"Mentioned by: {', '.join(mentioned_by)}")
        else:
            st.write("No items recorded")

    with col2:
        st.subheader("❌ What Didn't Go Well")
        didnt_go_well = summary.get("what_didnt_go_well", [])
        if didnt_go_well:
            for item in didnt_go_well:
                votes = item.get("votes")
                vote_str = f" ({votes} votes)" if votes else ""
                st.error(f"**{item.get('item', 'N/A')}**{vote_str}")
                mentioned_by = item.get("mentioned_by", [])
                if mentioned_by:
                    st.caption(f"Mentioned by: {', '.join(mentioned_by)}")
        else:
            st.write("No items recorded")

    st.divider()

    # Kudos
    kudos = summary.get("kudos", [])
    if kudos:
        st.subheader("🎉 Kudos")
        for k in kudos:
            st.info(f"**{k.get('from', 'Someone')}** → **{k.get('to', 'Someone')}**: {k.get('reason', '')}")
        st.divider()

    # Experiments to Try
    experiments = summary.get("experiments_to_try", [])
    if experiments:
        st.subheader("🧪 Experiments to Try")
        for exp in experiments:
            st.markdown(f"- {exp}")
        st.divider()

    # Action Items for Improvement
    display_action_items(summary.get("action_items", []))

    # Parking Lot
    parking_lot = summary.get("parking_lot", [])
    if parking_lot:
        st.divider()
        st.subheader("🅿️ Parking Lot")
        for item in parking_lot:
            st.caption(f"- {item}")

    st.divider()
    display_export_options(summary)


def display_one_on_one_summary(summary: dict):
    """Display 1-on-1 meeting summary."""
    display_common_header(summary)

    # Topics Discussed
    topics = summary.get("topics_discussed", [])
    if topics:
        st.subheader("💬 Topics Discussed")
        for topic in topics:
            with st.expander(f"📌 {topic.get('topic', 'Topic')}", expanded=True):
                st.write(topic.get("summary", "No summary"))
                initiated = topic.get("initiated_by")
                if initiated:
                    st.caption(f"Brought up by: {initiated}")
        st.divider()

    # Feedback Given
    feedback = summary.get("feedback_given", [])
    if feedback:
        st.subheader("💭 Feedback")
        for fb in feedback:
            fb_type = fb.get("type", "")
            icon = "👍" if fb_type == "positive" else "📝"
            st.markdown(f"{icon} **{fb.get('from', '?')}** → **{fb.get('to', '?')}**")
            st.write(fb.get("summary", ""))
        st.divider()

    # Career Development
    career = summary.get("career_development", {})
    if career and any(career.values()):
        st.subheader("🚀 Career Development")
        col1, col2 = st.columns(2)
        with col1:
            goals = career.get("goals_discussed", [])
            if goals:
                st.markdown("**Goals Discussed:**")
                for goal in goals:
                    st.markdown(f"- {goal}")
        with col2:
            growth = career.get("growth_areas", [])
            if growth:
                st.markdown("**Growth Areas:**")
                for area in growth:
                    st.markdown(f"- {area}")
        progress = career.get("progress_on_previous_goals")
        if progress:
            st.info(f"**Progress Update:** {progress}")
        st.divider()

    # Concerns and Support
    col1, col2 = st.columns(2)
    with col1:
        concerns = summary.get("concerns_raised", [])
        if concerns:
            st.subheader("⚠️ Concerns Raised")
            for concern in concerns:
                st.warning(concern)
    with col2:
        support = summary.get("support_needed", [])
        if support:
            st.subheader("🤝 Support Needed")
            for item in support:
                st.info(item)

    st.divider()
    display_action_items(summary.get("action_items", []))

    # Next Meeting Topics
    next_topics = summary.get("next_meeting_topics", [])
    if next_topics:
        st.divider()
        st.subheader("📅 Topics for Next Meeting")
        for topic in next_topics:
            st.markdown(f"- {topic}")

    st.divider()
    display_export_options(summary)


def display_client_summary(summary: dict):
    """Display client meeting summary."""
    display_common_header(summary)

    # Meeting Purpose
    purpose = summary.get("meeting_purpose")
    if purpose:
        st.info(f"**Meeting Purpose:** {purpose}")
        st.divider()

    # Client Requirements
    requirements = summary.get("client_requirements", [])
    if requirements:
        st.subheader("📋 Client Requirements")
        for req in requirements:
            priority = req.get("priority", "medium")
            badge = get_priority_badge(priority)
            st.markdown(f"**{req.get('requirement', 'N/A')}** {badge}")
            clarifications = req.get("clarifications_needed")
            if clarifications:
                st.caption(f"❓ Clarifications needed: {clarifications}")
        st.divider()

    # Commitments Made
    commitments = summary.get("commitments_made", [])
    if commitments:
        st.subheader("🤝 Commitments Made")
        for commit in commitments:
            deadline = commit.get("deadline")
            deadline_str = f" (by {deadline})" if deadline else ""
            st.success(f"**{commit.get('commitment', 'N/A')}**{deadline_str}")
            st.caption(f"Committed by: {commit.get('by_whom', 'Unknown')}")
        st.divider()

    # Concerns Raised
    concerns = summary.get("concerns_raised", [])
    if concerns:
        st.subheader("⚠️ Concerns Raised")
        for concern in concerns:
            resolved = concern.get("resolved", False)
            status = "✅ Resolved" if resolved else "🔄 Open"
            st.warning(f"**{concern.get('concern', 'N/A')}** - {status}")
            response = concern.get("response")
            if response:
                st.caption(f"Response: {response}")
        st.divider()

    # Decisions
    decisions = summary.get("decisions", [])
    if decisions:
        st.subheader("✅ Decisions")
        for decision in decisions:
            st.markdown(f"- **{decision.get('decision', 'N/A')}**")
            stakeholders = decision.get("stakeholders", [])
            if stakeholders:
                st.caption(f"Stakeholders: {', '.join(stakeholders)}")
        st.divider()

    display_action_items(summary.get("action_items", []))

    # Next Steps and Follow-up
    col1, col2 = st.columns(2)
    with col1:
        next_steps = summary.get("next_steps", [])
        if next_steps:
            st.subheader("➡️ Next Steps")
            for i, step in enumerate(next_steps, 1):
                st.markdown(f"{i}. {step}")
    with col2:
        follow_up = summary.get("follow_up_meeting")
        if follow_up:
            st.subheader("📅 Follow-up Meeting")
            st.info(follow_up)

    st.divider()
    display_export_options(summary)


def display_architecture_summary(summary: dict):
    """Display architecture review meeting summary."""
    display_common_header(summary)

    # Systems Discussed
    systems = summary.get("systems_discussed", [])
    if systems:
        st.markdown(f"**Systems Discussed:** {', '.join(systems)}")
        st.divider()

    # Technical Decisions
    decisions = summary.get("technical_decisions", [])
    if decisions:
        st.subheader("🏗️ Technical Decisions")
        for decision in decisions:
            with st.expander(f"📐 {decision.get('decision', 'Decision')}", expanded=True):
                rationale = decision.get("rationale")
                if rationale:
                    st.markdown(f"**Rationale:** {rationale}")

                alternatives = decision.get("alternatives_considered", [])
                if alternatives:
                    st.markdown("**Alternatives Considered:**")
                    for alt in alternatives:
                        st.markdown(f"- {alt}")

                trade_offs = decision.get("trade_offs", [])
                if trade_offs:
                    st.markdown("**Trade-offs:**")
                    for to in trade_offs:
                        st.warning(to)
        st.divider()

    # Architecture Changes
    changes = summary.get("architecture_changes", [])
    if changes:
        st.subheader("🔄 Architecture Changes")
        for change in changes:
            migration = "🔧 Migration needed" if change.get("migration_needed") else ""
            st.markdown(f"**{change.get('component', 'Component')}**: {change.get('change', 'N/A')} {migration}")
            impact = change.get("impact")
            if impact:
                st.caption(f"Impact: {impact}")
        st.divider()

    # Technical Debt
    tech_debt = summary.get("technical_debt_identified", [])
    if tech_debt:
        st.subheader("💳 Technical Debt Identified")
        for debt in tech_debt:
            severity = debt.get("severity", "medium")
            badge = get_priority_badge(severity)
            st.markdown(f"**{debt.get('item', 'N/A')}** {badge}")
            solution = debt.get("proposed_solution")
            if solution:
                st.caption(f"Proposed solution: {solution}")
        st.divider()

    # Open Technical Questions
    questions = summary.get("open_technical_questions", [])
    if questions:
        st.subheader("❓ Open Technical Questions")
        for q in questions:
            st.warning(q)
        st.divider()

    display_action_items(summary.get("action_items", []))

    # Diagrams/Docs Needed
    docs_needed = summary.get("diagrams_or_docs_needed", [])
    if docs_needed:
        st.divider()
        st.subheader("📄 Documentation Needed")
        for doc in docs_needed:
            st.markdown(f"- {doc}")

    st.divider()
    display_export_options(summary)


def display_presentation_summary(summary: dict):
    """Display presentation meeting summary."""
    display_common_header(summary)

    # Presenter and Title
    presenter = summary.get("presenter")
    title = summary.get("presentation_title")
    if presenter or title:
        col1, col2 = st.columns(2)
        with col1:
            if presenter:
                st.markdown(f"**🎤 Presenter:** {presenter}")
        with col2:
            if title:
                st.markdown(f"**📊 Title:** {title}")
        st.divider()

    # Purpose of Presentation
    purpose = summary.get("purpose_of_presentation")
    if purpose:
        st.subheader("🎯 Purpose")
        st.info(purpose)
        st.divider()

    # Executive Overview
    overview = summary.get("executive_overview")
    if overview:
        st.subheader("📋 Executive Overview")
        st.write(overview)
        st.divider()

    # Key Topics Presented
    topics = summary.get("key_topics_presented", [])
    if topics:
        st.subheader("📚 Key Topics")
        for topic in topics:
            with st.expander(f"📌 {topic.get('topic', 'Topic')}", expanded=True):
                st.write(topic.get("summary", ""))
                takeaways = topic.get("key_takeaways", [])
                if takeaways:
                    st.markdown("**Key Takeaways:**")
                    for t in takeaways:
                        st.markdown(f"- {t}")
        st.divider()

    # Demonstrations / Walkthroughs
    demos = summary.get("demonstrations_walkthroughs", [])
    if demos:
        st.subheader("🖥️ Demonstrations / Walkthroughs")
        for demo in demos:
            st.markdown(f"**{demo.get('title', 'Demo')}**")
            description = demo.get("description")
            if description:
                st.write(description)
            outcome = demo.get("outcome")
            if outcome:
                st.success(f"Outcome: {outcome}")
        st.divider()

    # Q&A
    qna = summary.get("questions_and_answers", [])
    if qna:
        st.subheader("❓ Questions & Answers")
        for qa in qna:
            asked_by = qa.get("asked_by")
            asked_str = f" (asked by {asked_by})" if asked_by else ""
            st.markdown(f"**Q:** {qa.get('question', 'N/A')}{asked_str}")
            st.markdown(f"**A:** {qa.get('answer', 'N/A')}")
            if qa.get("follow_up_needed"):
                st.warning("⚠️ Follow-up needed")
            st.markdown("---")
        st.divider()

    # Decisions or Agreements
    decisions = summary.get("decisions_or_agreements", [])
    if decisions:
        st.subheader("✅ Decisions / Agreements")
        for decision in decisions:
            st.markdown(f"- **{decision.get('decision', 'N/A')}**")
            stakeholders = decision.get("stakeholders", [])
            if stakeholders:
                st.caption(f"Stakeholders: {', '.join(stakeholders)}")
        st.divider()

    # Action Items
    display_action_items(summary.get("action_items", []))

    # Resources Shared
    resources = summary.get("resources_shared", [])
    if resources:
        st.divider()
        st.subheader("📎 Resources Shared")
        for resource in resources:
            if isinstance(resource, dict):
                res_name = resource.get("resource", "Resource")
                res_type = resource.get("type", "")
                res_loc = resource.get("location")
                type_badge = f"[{res_type}]" if res_type else ""
                if res_loc and res_loc.startswith("http"):
                    st.markdown(f"- {type_badge} [{res_name}]({res_loc})")
                elif res_loc:
                    st.markdown(f"- {type_badge} **{res_name}**: {res_loc}")
                else:
                    st.markdown(f"- {type_badge} {res_name}")
            else:
                st.markdown(f"- {resource}")

    st.divider()
    display_export_options(summary)


def display_general_summary(summary: dict):
    """Display general meeting summary (default)."""
    display_common_header(summary)

    # Action Items
    display_action_items(summary.get("action_items", []))
    st.divider()

    # Speaker Summary (enhanced feature)
    attendees = summary.get("attendees", [])
    if attendees and isinstance(attendees[0], dict) and attendees[0].get("contribution_summary"):
        st.subheader("Speaker Contributions")
        for attendee in attendees:
            name = attendee.get("name", "Unknown")
            role = attendee.get("role", "")
            contribution = attendee.get("contribution_summary", "")
            role_str = f" ({role})" if role else ""
            with st.expander(f"{name}{role_str}", expanded=False):
                st.write(contribution if contribution else "No specific contributions noted.")
        st.divider()

    # Key Decisions
    decisions = summary.get("decisions", [])
    if decisions:
        st.subheader("Key Decisions")
        for decision in decisions:
            st.markdown(f"- **{decision.get('decision', 'N/A')}**")
            if decision.get("context"):
                st.markdown(f"  - _{decision['context']}_")

    # Key Topics
    topics = summary.get("key_topics", [])
    if topics:
        st.subheader("Key Topics")
        for topic in topics:
            st.markdown(f"- {topic}")

    # Open Questions
    questions = summary.get("open_questions", [])
    if questions:
        st.subheader("Open Questions")
        st.warning("\n".join([f"- {q}" for q in questions]))

    # Next Steps
    next_steps = summary.get("next_steps", [])
    if next_steps:
        st.subheader("Next Steps")
        for i, step in enumerate(next_steps, 1):
            st.markdown(f"{i}. {step}")

    # Notable Quotes (enhanced feature)
    quotes = summary.get("notable_quotes", [])
    if quotes:
        st.subheader("Notable Quotes")
        for quote in quotes[:5]:  # Limit to top 5
            speaker = quote.get("speaker", "Unknown")
            text = quote.get("quote", "")
            significance = quote.get("significance") or quote.get("context", "")
            st.markdown(f"> \"{text}\" - **{speaker}**")
            if significance:
                st.caption(significance)

    st.divider()
    display_export_options(summary)


def display_summary(summary: dict):
    """Display the meeting summary in a formatted layout based on meeting type."""
    meeting_type = summary.get("meeting_type", "general")

    # Route to the appropriate display function based on meeting type
    display_functions = {
        "standup": display_standup_summary,
        "sprint_planning": display_sprint_planning_summary,
        "retrospective": display_retrospective_summary,
        "one_on_one": display_one_on_one_summary,
        "client": display_client_summary,
        "architecture": display_architecture_summary,
        "presentation": display_presentation_summary,
        "general": display_general_summary,
    }

    display_func = display_functions.get(meeting_type, display_general_summary)
    display_func(summary)


def process_transcript(transcript: str, api_key: str, progress_container, meeting_type: str = None):
    """Process the transcript and update session state."""
    # Clear previous results
    st.session_state.summary = None
    st.session_state.error = None
    st.session_state.processing_info = None

    # Preprocess transcript (handles VTT parsing automatically)
    transcript, vtt_duration = preprocess_transcript(transcript)

    # Validate transcript
    is_valid, error_msg = validate_transcript(transcript)
    if not is_valid:
        st.session_state.error = error_msg
        return

    # Process with pipeline
    try:
        client = LangbaseClient(api_key)
        pipeline = MeetingPipeline(client)

        # Get processing estimate
        estimate = pipeline.estimate_processing(transcript)
        estimate["vtt_duration"] = vtt_duration  # Add VTT duration if available
        st.session_state.processing_info = estimate

        # Create progress UI
        progress_bar = progress_container.progress(0)
        status_text = progress_container.empty()

        def update_progress(current: int, total: int, message: str):
            if total > 0:
                progress_bar.progress(current / total)
            status_text.text(message)

        # Run the pipeline
        result = pipeline.process(transcript, progress_callback=update_progress, meeting_type=meeting_type)

        # Override duration with VTT duration if available
        summary = result.summary
        if vtt_duration:
            summary["duration_estimate"] = vtt_duration

        # Add meeting type to summary
        if meeting_type:
            meeting_type_enum = MeetingType(meeting_type)
            summary["meeting_type"] = meeting_type
            summary["meeting_type_display"] = get_meeting_type_display_name(meeting_type_enum)

        st.session_state.summary = summary
        st.session_state.processing_info = {
            **estimate,
            "chunks_processed": result.chunks_processed,
            "was_chunked": result.was_chunked
        }

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

    except Exception as e:
        st.session_state.error = str(e)


def main():
    """Main application entry point."""
    # Header
    st.title("📋 Meeting Summary Agent")
    st.markdown("Transform meeting transcripts into actionable summaries")

    # Check for API key
    api_key = get_api_key()
    if not api_key:
        st.error(
            "⚠️ No API key found. Please set `LANGBASE_API_KEY` in your environment variables "
            "or Streamlit secrets. See the README for setup instructions."
        )
        st.stop()

    # Main layout
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Input")
        transcript = st.text_area(
            "Paste your meeting transcript here:",
            height=400,
            placeholder="Meeting: Q4 Planning Session\nDate: December 10, 2024\nAttendees: Sarah (PM), John (Engineering Lead)...\n\nSarah: Good morning everyone...",
            key="transcript_input"
        )

        # Show character count and chunking info
        if transcript:
            char_count = len(transcript)
            token_estimate = estimate_tokens(transcript)
            chunk_estimate = max(1, char_count // 12000)  # ~3000 tokens per chunk
            info_text = f"📊 {char_count:,} characters (~{token_estimate:,} tokens)"
            if is_vtt_content(transcript):
                # Parse VTT to get duration preview
                _, preview_duration = preprocess_transcript(transcript)
                vtt_info = "🎬 VTT format detected"
                if preview_duration:
                    vtt_info += f" ({preview_duration})"
                info_text = vtt_info + " | " + info_text
            if chunk_estimate > 1:
                info_text += f" | Will process in {chunk_estimate} chunks"
            st.caption(info_text)

            # Meeting type detection
            transcript_hash = hash(transcript)
            if st.session_state.last_transcript_hash != transcript_hash:
                # Transcript changed, re-detect meeting type
                preprocessed, _ = preprocess_transcript(transcript)
                detection_result = detect_meeting_type(preprocessed)
                st.session_state.detected_meeting_type = detection_result
                st.session_state.selected_meeting_type = detection_result.meeting_type.value
                st.session_state.last_transcript_hash = transcript_hash

            # Display meeting type selection
            if st.session_state.detected_meeting_type:
                detection = st.session_state.detected_meeting_type
                confidence_pct = int(detection.confidence * 100)

                st.markdown("---")
                st.markdown("**Meeting Type**")

                # Get all meeting types for dropdown
                all_types = get_all_meeting_types()
                type_options = [display_name for _, display_name in all_types]
                type_values = [value for value, _ in all_types]

                # Find current selection index
                current_value = st.session_state.selected_meeting_type
                current_index = type_values.index(current_value) if current_value in type_values else 0

                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_display = st.selectbox(
                        "Select meeting type:",
                        options=type_options,
                        index=current_index,
                        key="meeting_type_selector",
                        label_visibility="collapsed"
                    )
                    # Update selected type
                    selected_index = type_options.index(selected_display)
                    st.session_state.selected_meeting_type = type_values[selected_index]

                with col2:
                    # Show confidence badge
                    if confidence_pct >= 70:
                        st.success(f"{confidence_pct}%")
                    elif confidence_pct >= 50:
                        st.warning(f"{confidence_pct}%")
                    else:
                        st.error(f"{confidence_pct}%")

                # Show detection signals in expander
                with st.expander("Detection details", expanded=False):
                    for signal in detection.signals:
                        st.caption(f"• {signal}")
                    if detection.keyword_matches:
                        matched_types = [k for k, v in detection.keyword_matches.items() if v]
                        if matched_types:
                            st.caption(f"Keywords matched for: {', '.join(matched_types)}")

        # Progress container (placed before button for visual flow)
        progress_container = st.container()

        # Submit button
        if st.button("✨ Summarize Meeting", type="primary", use_container_width=True):
            meeting_type = st.session_state.get("selected_meeting_type")
            process_transcript(transcript, api_key, progress_container, meeting_type)

    with right_col:
        st.subheader("Summary")

        # Display error if present
        if st.session_state.error:
            st.error(f"❌ {st.session_state.error}")

        # Display processing info if available
        processing_info = st.session_state.processing_info
        if processing_info and processing_info.get("was_chunked"):
            st.caption(f"Processed in {processing_info.get('chunks_processed', 0)} chunks")

        # Display summary if present
        if st.session_state.summary:
            display_summary(st.session_state.summary)
        elif not st.session_state.error:
            st.markdown(
                """
                <div style="
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    color: #888;
                    margin-top: 20px;
                ">
                    <p style="font-size: 18px;">📝 Your summary will appear here</p>
                    <p>Paste a transcript and click "Summarize Meeting"</p>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
