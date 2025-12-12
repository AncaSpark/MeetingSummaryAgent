Identify the meeting type to apply specialized summarization:

**Detection Criteria:**

1. **Sprint Planning**
   - Keywords: sprint, story points, backlog, velocity, sprint goal, user stories, commitment, estimation, capacity
   - Typical duration: 2-4 hours
   - Indicators: Discussion of work items, estimations, capacity planning, story refinement

2. **Standup/Daily Scrum**
   - Keywords: yesterday, today, tomorrow, blockers, impediments, status update, daily
   - Typical duration: 15 minutes
   - Indicators: Round-robin updates, brief status reports, sequential speaker pattern

3. **Retrospective**
   - Keywords: what went well, what didn't, action items, improve, lessons learned, retro, iteration, reflection
   - Typical duration: 1-2 hours
   - Indicators: Reflection on past work, team discussion about process, improvement focus

4. **1-on-1**
   - Participant count: Exactly 2 people
   - Keywords: career, feedback, goals, development, concerns, support, growth, performance, 1:1, one-on-one
   - Indicators: Personal/professional development discussion, private conversation

5. **Client Meeting**
   - Keywords: client, stakeholder, proposal, requirements, deliverables, timeline, contract, proposal, engagement
   - Indicators: External stakeholder involvement, formal tone, business-focused discussion

6. **Architecture Review**
   - Keywords: architecture, design, technical, scalability, patterns, infrastructure, system, component, integration
   - Indicators: Technical diagrams mentioned, system design discussion, technology decisions

7. **Presentation**
   - Keywords: presentation, demo, walkthrough, showcase, slides, deck, overview, introduce, presenting, show you
   - Typical duration: 30-90 minutes
   - Indicators: Single presenter dominates speaking time, Q&A section, demos or walkthroughs, resources/materials shared

8. **General Meeting**
   - Default when no specific pattern matches strongly
   - Use standard summarization approach for any business meeting

**Detection Method:**
- Analyze meeting title first (often contains type keywords)
- Check participant count (2 = likely 1-on-1)
- Examine meeting duration (15 min = likely standup, 2-4 hours = likely planning/retro)
- Scan first 20% of transcript for keyword patterns
- Look for structural indicators (round-robin pattern = standup, systematic format = specific type)
- Calculate confidence score based on multiple signals
- When confidence < 70%, default to "General Meeting" format or ask user to confirm
- Allow users to manually specify meeting type if auto-detection is incorrect

### Step 2.6: Confirm Meeting Type (Optional)

When detection confidence is uncertain (< 70%):

**Ask the user:**
> "Based on my analysis, this appears to be a [DETECTED_TYPE] meeting (confidence: [XX%]). Is this correct?
>
> Available types: Sprint Planning, Standup, Retrospective, 1-on-1, Client Meeting, Architecture Review, Presentation, General."

**If user provides different type:**
- Use the user-specified template
- Learn from the correction for future improvements

**If user confirms:**
- Proceed with detected template

### Step 3: Analyze Content

Identify and extract:

1. **Main Topics Discussed**
   - Group related conversation threads
   - Identify primary themes
   - Note discussion flow

2. **Key Decisions Made**
   - Explicit decisions stated in the meeting
   - Agreements reached
   - Directions chosen

3. **Action Items**
   - Tasks assigned to specific people
   - Deadlines mentioned
   - Follow-up activities

4. **Questions & Concerns**
   - Unresolved issues
   - Questions that need follow-up
   - Concerns raised

5. **Important Notes**
   - Critical information shared
   - Resources mentioned
   - Links or references

### Step 4: Generate Summary

Create a structured summary with these sections:

```markdown
# Meeting Summary: [Meeting Title]

**Type:** [Meeting Type]
**Date:** [Date]
**Duration:** [Duration]
**Attendees:** [List of participants]

## Executive Summary
[2-3 sentence overview of the meeting]

## Key Topics Discussed
- [Topic 1]: [Brief description]
- [Topic 2]: [Brief description]
- [Topic 3]: [Brief description]

## Decisions Made
1. [Decision 1]
2. [Decision 2]
3. [Decision 3]

## Action Items
| Action Item | Owner | Deadline |
|-------------|-------|----------|
| [Task 1] | [Person] | [Date] |
| [Task 2] | [Person] | [Date] |

## Open Questions
- [Question 1]
- [Question 2]

## Next Steps
- [Next step 1]
- [Next step 2]

## Additional Notes
[Any other important information]
```
## Meeting Type Templates

Use these specialized templates based on the detected meeting type:

### Template 1: Sprint Planning

```markdown
# Sprint Planning Summary: [Sprint Name/Number]

**Type:** Sprint Planning
**Date:** [Date]
**Duration:** [Duration]
**Attendees:** [Team members]
**Sprint Duration:** [e.g., 2 weeks]
**Sprint Goal:** [High-level objective for the sprint]

## Sprint Objective
[1-2 sentences describing the primary goal for this sprint]

## Sprint Capacity
- **Total Story Points Committed:** [Number]
- **Team Velocity (Previous Sprint):** [Number]
- **Team Capacity:** [Number of days/person]
- **Planned Capacity:** [Accounting for PTO, holidays]

## User Stories Committed
| Story ID | Description | Story Points | Assignee | Priority |
|----------|-------------|--------------|----------|----------|
| [ID] | [Brief description] | [Points] | [Name] | High/Med/Low |

## Backlog Refinement Notes
- [Stories discussed but not committed]
- [Stories that need more refinement]
- [Dependencies identified]

## Technical Considerations
- [Architecture decisions]
- [Technical dependencies]
- [Infrastructure needs]

## Risks & Concerns
- [Risk 1 and mitigation plan]
- [Risk 2 and mitigation plan]

## Definition of Done
- [Criteria for story completion]
- [Quality standards]
- [Documentation requirements]

## Action Items
| Action Item | Owner | Deadline |
|-------------|-------|----------|
| [Task] | [Person] | [Date] |

## Next Sprint Planning
**Date:** [Date of next planning session]
```

### Template 2: Standup/Daily Scrum

```markdown
# Daily Standup: [Date]

**Type:** Daily Standup
**Date:** [Date]
**Duration:** [Duration]
**Attendees:** [Team members]

## Team Updates

### [Team Member 1]
**Yesterday:**
- [Completed items]

**Today:**
- [Planned work]

**Blockers:**
- [Any impediments or NONE]

### [Team Member 2]
**Yesterday:**
- [Completed items]

**Today:**
- [Planned work]

**Blockers:**
- [Any impediments or NONE]

[Repeat for each team member]

## Sprint Progress
- **Sprint:** [Sprint name/number]
- **Days Remaining:** [Number]
- **Stories Completed:** [X of Y]
- **Stories In Progress:** [Number]

## Blockers Requiring Action
| Blocker | Affected Person | Action Needed | Owner |
|---------|----------------|---------------|--------|
| [Issue] | [Name] | [What's needed] | [Who will resolve] |

## Follow-up Items
- [Items that need offline discussion]
- [Topics deferred to other meetings]

## Notes
- [Any important announcements]
- [Team events or changes]
```

### Template 3: Retrospective

```markdown
# Sprint Retrospective: [Sprint Name/Number]

**Type:** Retrospective
**Date:** [Date]
**Duration:** [Duration]
**Attendees:** [Team members]
**Sprint Reviewed:** [Sprint identifier]

## Sprint Metrics
- **Stories Committed:** [Number]
- **Stories Completed:** [Number]
- **Completion Rate:** [Percentage]
- **Velocity:** [Story points]

## What Went Well ✅
1. [Positive item 1]
   - *Impact:* [How this helped the team]
2. [Positive item 2]
   - *Impact:* [How this helped the team]
3. [Positive item 3]
   - *Impact:* [How this helped the team]

## What Didn't Go Well ❌
1. [Challenge 1]
   - *Impact:* [How this affected the team]
   - *Root Cause:* [Why this happened]
2. [Challenge 2]
   - *Impact:* [How this affected the team]
   - *Root Cause:* [Why this happened]
3. [Challenge 3]
   - *Impact:* [How this affected the team]
   - *Root Cause:* [Why this happened]

## Lessons Learned
- [Key takeaway 1]
- [Key takeaway 2]
- [Key takeaway 3]

## Action Items for Improvement
| Action Item | Expected Outcome | Owner | Deadline | Priority |
|-------------|------------------|-------|----------|----------|
| [Action] | [What will improve] | [Person] | [Date] | High/Med/Low |

## Experiments to Try
- [Process change 1 to test next sprint]
- [Tool or practice to experiment with]

## Kudos & Recognitions
- [Team member recognition]
- [Highlight of great work]

## Next Retrospective
**Date:** [Date of next retro]
**Format:** [Any changes to format]
```

### Template 4: 1-on-1 Meeting

```markdown
# 1-on-1: [Manager] & [Team Member]

**Type:** 1-on-1
**Date:** [Date]
**Duration:** [Duration]

## Topics Discussed

### Current Work & Projects
- [Project/task updates]
- [Challenges or concerns]
- [Wins and accomplishments]

### Career Development
- **Short-term Goals (3-6 months):**
  - [Goal 1]
  - [Goal 2]

- **Long-term Goals (1+ years):**
  - [Goal 1]
  - [Goal 2]

- **Skills to Develop:**
  - [Skill 1]
  - [Skill 2]

### Feedback Exchange
**Feedback to Team Member:**
- [Positive feedback]
- [Areas for improvement]
- [Specific examples]

**Feedback from Team Member:**
- [What's working well]
- [Concerns or suggestions]
- [Support needed]

### Team & Process
- [Team dynamics discussion]
- [Process improvement ideas]
- [Resources needed]

### Personal Well-being
- [Work-life balance check]
- [Workload assessment]
- [Any personal concerns affecting work]

## Commitments & Action Items
| Action Item | Owner | Deadline | Category |
|-------------|-------|----------|----------|
| [Action] | [Person] | [Date] | Development/Project/Support |

## Follow-up Topics for Next Time
- [Topic to revisit]
- [Goal progress check-in]

## Next Meeting
**Date:** [Scheduled date]
**Proposed Topics:** [Items for agenda]

## Private Notes
[Confidential notes - handle with care when sharing summaries]
```

### Template 5: Client Meeting

```markdown
# Client Meeting: [Meeting Title]

**Type:** Client Meeting
**Date:** [Date]
**Duration:** [Duration]
**Attendees:** [Internal and external participants]
**Client:** [Client name/organization]

## Meeting Purpose
[Why this meeting was held]

## Executive Summary
[2-3 sentence overview for stakeholders]

## Discussion Topics

### 1. [Topic Name]
**Context:** [Background information]
**Discussion:** [Key points discussed]
**Client Perspective:** [Client's views, concerns, or requests]
**Our Response:** [How we responded or what we proposed]

### 2. [Topic Name]
**Context:** [Background information]
**Discussion:** [Key points discussed]
**Client Perspective:** [Client's views, concerns, or requests]
**Our Response:** [How we responded or what we proposed]

## Client Requirements
| Requirement | Priority | Feasibility | Owner | Target Date |
|-------------|----------|-------------|-------|-------------|
| [Requirement] | High/Med/Low | [Assessment] | [Person] | [Date] |

## Decisions Made
1. [Decision 1]
   - *Rationale:* [Why this was decided]
   - *Impact:* [What this affects]
2. [Decision 2]
   - *Rationale:* [Why this was decided]
   - *Impact:* [What this affects]

## Action Items
| Action Item | Owner (Internal/Client) | Deadline | Status |
|-------------|-------------------------|----------|--------|
| [Action] | [Person] | [Date] | Pending/In Progress |

## Commitments to Client
- [What we promised to deliver]
- [Timeline commitments]
- [Quality assurances]

## Client Concerns & Risks
- [Concern 1]: [Our mitigation approach]
- [Concern 2]: [Our mitigation approach]

## Next Steps
- [Immediate next actions]
- [Follow-up communications planned]
- [Deliverable schedule]

## Next Meeting
**Date:** [Date]
**Agenda:** [Topics for next discussion]

## Internal Notes
[Private notes about client relationship, concerns, or strategy]
```

### Template 6: Architecture Review

```markdown
# Architecture Review: [System/Component Name]

**Type:** Architecture Review
**Date:** [Date]
**Duration:** [Duration]
**Attendees:** [Architects, engineers, stakeholders]
**Presenter:** [Who presented the design]

## Architecture Overview
[High-level description of the proposed architecture]

## Business Context
- **Problem Statement:** [What problem does this solve]
- **Business Goals:** [Why this architecture is needed]
- **Success Criteria:** [How we measure success]

## Architecture Components

### System Design
- **Key Components:** [List major components]
- **Technologies:** [Tech stack and tools]
- **Integration Points:** [How it connects to existing systems]

### Architecture Diagram
[Note: Diagram was discussed/shared during meeting]
**Location:** [Where diagram is stored]

## Technical Decisions

### Decision 1: [Decision Name]
- **Options Considered:** [Alternative approaches]
- **Decision:** [What was chosen]
- **Rationale:** [Why this approach]
- **Trade-offs:** [Pros and cons]

### Decision 2: [Decision Name]
- **Options Considered:** [Alternative approaches]
- **Decision:** [What was chosen]
- **Rationale:** [Why this approach]
- **Trade-offs:** [Pros and cons]

## Non-Functional Requirements

| Requirement | Target | Approach | Validation Method |
|-------------|--------|----------|-------------------|
| Scalability | [e.g., 10K RPS] | [How achieved] | [How tested] |
| Availability | [e.g., 99.9%] | [How achieved] | [How measured] |
| Security | [Requirements] | [Implementation] | [Validation] |
| Performance | [Targets] | [Optimization strategy] | [Benchmarks] |

## Risks & Mitigations
| Risk | Impact | Probability | Mitigation Strategy | Owner |
|------|--------|-------------|---------------------|-------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to mitigate] | [Person] |

## Technical Debt & Concerns
- [Debt item 1]: [Plan to address]
- [Concern 1]: [Resolution approach]

## Dependencies
- **Internal:** [Other teams or systems]
- **External:** [Third-party services or tools]
- **Timeline Impact:** [How dependencies affect delivery]

## Implementation Plan
| Phase | Deliverables | Timeline | Owner |
|-------|--------------|----------|-------|
| Phase 1 | [What's built] | [Dates] | [Team/Person] |

## Open Questions
- [Technical question 1]: [Who will investigate]
- [Question 2]: [Who will investigate]

## Action Items
| Action Item | Owner | Deadline | Type |
|-------------|-------|----------|------|
| [Action] | [Person] | [Date] | Research/POC/Implementation |

## Approval Status
- **Approved:** [Yes/No/Conditional]
- **Conditions:** [Any conditions for approval]
- **Approvers:** [Who approved]

## Next Steps
- [Follow-up reviews scheduled]
- [POC or prototype work]
- [Documentation to be created]

## References
- [Architecture decision records]
- [Related design documents]
- [Technical specifications]
```

### Template 7: Presentation

```markdown
# Presentation Summary: [Title]

**Type:** Presentation
**Date:** [Date]
**Duration:** [Duration]
**Presenter(s):** [Name(s)]
**Attendees:** [List]

## Purpose of the Presentation
[Brief explanation of why this presentation was held]

## Executive Overview
[2–3 sentences describing the core message or outcome of the presentation]

## Key Topics Presented
- **[Topic 1]**
  [Short explanation of what the presenter covered]

- **[Topic 2]**
  [Short explanation]

- **[Topic 3]**
  [Short explanation]

## Demonstrations / Walkthroughs
- [Demo or walkthrough name]
  **Details:** [What was shown, key insights]

## Questions & Answers
| Question | Asked By | Response |
|---------|----------|----------|
| [Question] | [Name] | [Summary of answer] |

## Decisions or Agreements (If Any)
1. [Decision or alignment outcome]
2. [Decision]

## Action Items
| Action Item | Owner | Deadline |
|-------------|-------|----------|
| [Task 1] | [Person] | [Date] |
| [Task 2] | [Person] | [Date] |

## Resources Shared
- [Link / document / deck name]
- [Additional materials]

## Next Steps
- [Follow-up action or scheduled follow-up meeting]

## Additional Notes
[Any other important information delivered during the presentation]
```

### Template Selection Guide

**Use the appropriate template based on meeting type detection:**
- Sprint Planning → Template 1
- Standup → Template 2
- Retrospective → Template 3
- 1-on-1 → Template 4
- Client Meeting → Template 5
- Architecture Review → Template 6
- Presentation → Template 7
- General/Unknown → Use the standard template (Step 4)

## Common Use Cases

### Use Case 0: Type-Specific Summaries

Automatically detect meeting type and apply specialized templates:

**Focus on:**
- Meeting type detection based on keywords, duration, participant count, and structure
- Type-specific sections and emphasis (e.g., story points for sprint planning, yesterday/today/blockers for standups)
- Relevant metrics for each meeting type
- Format optimized for meeting purpose and audience

**When to use:**
- Meeting follows a standard format (standup, sprint planning, retrospective, etc.)
- Audience expects specific information based on meeting type
- Meeting has recurring structure that matches a template
- You want specialized formatting beyond the general template

**Example:** A daily standup automatically uses the standup template with yesterday/today/blockers format instead of the general meeting format.

### Use Case 1: Quick Summary for Non-Attendees

Generate a brief summary for stakeholders who didn't attend:

**Focus on:**
- Executive summary (1-2 paragraphs)
- Key decisions only
- Critical action items

### Use Case 2: Detailed Meeting Minutes

Create comprehensive meeting minutes for official records:

**Focus on:**
- Complete attendee list
- Detailed topic discussions
- Verbatim decisions
- All action items with assignments

### Use Case 3: Action Item Extraction

Extract only actionable tasks for task tracking systems:

**Focus on:**
- Action items with clear owners
- Deadlines
- Dependencies
- Format for import (CSV, JSON, etc.)

### Use Case 4: Follow-up Email Draft

Create a follow-up email summarizing the meeting:

**Focus on:**
- Professional email format
- Thank attendees
- Recap key points
- List action items
- Invite questions or clarifications

## Advanced Usage

### Handling Multiple Speakers

Teams transcripts include speaker labels:
```
John Doe: I think we should proceed with option A.
Jane Smith: I agree, but we need to consider the timeline.
```

- Group comments by speaker when relevant
- Identify who made key decisions
- Track action item assignments

### Extracting Timestamps

Teams transcripts may include timestamps:
```
[10:05 AM] John Doe: Let's discuss the project timeline.
```

- Use timestamps to track meeting flow
- Reference specific moments for important decisions
- Calculate time spent on each topic

### Sentiment Analysis (Optional)

For team health insights:
- Identify positive or negative sentiment
- Note areas of agreement vs. disagreement
- Flag potential conflicts or concerns

### Integration with Task Management

Format action items for common tools:

**For Jira:**
```markdown
- **Summary:** [Action item]
- **Assignee:** [Person]
- **Due Date:** [Date]
- **Description:** [Context from meeting]
```

**For Microsoft Planner/To Do:**
```json
{
  "title": "[Action item]",
  "assignedTo": "[Person]",
  "dueDate": "[Date]",
  "notes": "[Context]"
}
```

### Meeting Type Detection Logic

Implement intelligent type detection using multiple signals:

**Detection Algorithm:**
1. Check participant count (2 = likely 1-on-1)
2. Analyze meeting title for type keywords
3. Examine meeting duration (15 min = likely standup, 2-4 hours = likely planning/retro)
4. Scan first 20% of transcript for keyword patterns
5. Look for structural indicators (round-robin speaking = standup, systematic format = specific type)
6. Calculate confidence score by combining multiple signals
7. If confidence < 70%, default to "General Meeting" or ask user to confirm
8. Allow manual override of detected type

**Confidence Scoring:**
- **High Confidence (90%+):** 3+ keyword matches + clear structural pattern + duration match
- **Medium Confidence (70-89%):** 2 keyword matches OR clear structural pattern
- **Low Confidence (<70%):** 1 keyword match, unclear structure → use General template or ask user

**Keyword Patterns by Meeting Type:**

```python
meeting_type_keywords = {
    "sprint_planning": [
        "sprint", "story points", "backlog", "velocity", "commitment",
        "sprint goal", "user stories", "estimation", "capacity", "planning poker"
    ],
    "standup": [
        "yesterday", "today", "tomorrow", "blockers", "impediments",
        "status update", "daily", "scrum", "working on", "plan to"
    ],
    "retrospective": [
        "went well", "didn't work", "improve", "action items", "lessons learned",
        "retro", "iteration", "reflection", "what worked", "continue doing", "stop doing"
    ],
    "one_on_one": [
        "career", "feedback", "goals", "development", "concerns", "support",
        "growth", "performance", "1:1", "one-on-one", "coaching", "mentoring"
    ],
    "client": [
        "client", "stakeholder", "proposal", "requirements", "deliverables",
        "timeline", "contract", "engagement", "scope", "budget"
    ],
    "architecture": [
        "architecture", "design", "technical", "scalability", "patterns",
        "infrastructure", "system", "component", "integration", "microservices",
        "deployment", "database", "API"
    ],
    "presentation": [
        "presentation", "demo", "walkthrough", "showcase", "slides", "deck",
        "overview", "introduce", "presenting", "show you", "let me show",
        "questions at the end", "Q&A", "any questions"
    ]
}
```

**Decision Tree:**

```
START
│
├─ Participant Count = 2?
│  └─ YES → Check for career/feedback/goals keywords
│     ├─ Found → 1-ON-1 (High Confidence)
│     └─ Not Found → Check other patterns → Continue
│  └─ NO → Continue
│
├─ Duration ≤ 20 minutes + Round-robin structure detected?
│  └─ YES → Check for yesterday/today/blockers keywords
│     ├─ Found → STANDUP (High Confidence)
│     └─ Not Found → Continue
│  └─ NO → Continue
│
├─ Keywords: "sprint", "story points", "backlog", "velocity" (3+ matches)?
│  └─ YES → SPRINT PLANNING (High Confidence)
│  └─ NO → Continue
│
├─ Keywords: "went well", "didn't work", "improve", "lessons" (3+ matches)?
│  └─ YES → RETROSPECTIVE (High Confidence)
│  └─ NO → Continue
│
├─ Keywords: "architecture", "design", "scalability", "system" (3+ matches)?
│  └─ YES → ARCHITECTURE REVIEW (Medium-High Confidence)
│  └─ NO → Continue
│
├─ External participants OR client/stakeholder keywords (2+ matches)?
│  └─ YES → CLIENT MEETING (Medium Confidence)
│  └─ NO → Continue
│
├─ Keywords: "presentation", "demo", "slides", "showcase" (2+ matches) + Single dominant speaker?
│  └─ YES → PRESENTATION (Medium-High Confidence)
│  └─ NO → Continue
│
└─ DEFAULT → GENERAL MEETING
   (Use when confidence < 70% for any specific type)
```

**Structural Pattern Detection:**

- **Round-robin pattern:** Sequential speakers giving brief updates → Likely standup
- **Systematic format:** Repeated structure across speakers → Likely standup or retro
- **Technical deep-dive:** Heavy technical terminology, diagrams mentioned → Likely architecture review
- **Two-person dialogue:** Extended back-and-forth between two people → Likely 1-on-1
- **Story/task discussion:** Multiple items discussed with estimation → Likely sprint planning
- **Single dominant speaker:** One person speaks 70%+ of the time, followed by Q&A → Likely presentation

**Fallback Behavior:**

When to use General Meeting template:
- Detection confidence < 70%
- User explicitly requests generic format
- Meeting doesn't fit standard patterns
- Multiple meeting types mixed in one session (hybrid meeting)
- User prefers simple format over specialized
- Meeting is ad-hoc or one-off without clear structure

The General Meeting template is the default safe choice that works for any meeting.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for complete meeting summarization examples.

## Best Practices

### DO:
- ✅ Read the entire transcript before summarizing
- ✅ Detect meeting type for specialized formatting
- ✅ Use type-appropriate sections and emphasis
- ✅ Include meeting-specific metrics (velocity for sprints, completion rate for retros)
- ✅ Preserve exact wording for decisions and commitments
- ✅ Assign action items to specific individuals
- ✅ Include deadlines when mentioned
- ✅ Use clear, concise language
- ✅ Structure information logically
- ✅ Highlight urgent or critical items
- ✅ Ask user to confirm if meeting type detection is uncertain (<70% confidence)

### DON'T:
- ❌ Miss action items or decisions
- ❌ Force a meeting type when detection is uncertain
- ❌ Use wrong template for meeting type
- ❌ Include irrelevant sections from generic template
- ❌ Paraphrase decisions inaccurately
- ❌ Omit important context
- ❌ Create action items that weren't explicitly stated
- ❌ Ignore unresolved questions
- ❌ Make assumptions about deadlines

### Meeting Type Selection Tips

**Help the system detect correctly:**
- Use descriptive meeting titles ("Sprint 23 Planning" vs "Team Meeting")
- Follow standard formats when possible (standup: yesterday/today/blockers)
- Include meeting type in calendar invite or transcript title
- Use consistent terminology within your team

**When detection is wrong:**
- Manually specify the type when asked
- Provide feedback to improve future detection
- Consider if "General Meeting" is more appropriate for non-standard meetings
- Remember you can always override auto-detection

## Troubleshooting

### Issue: Transcript is poorly formatted
**Solution:** Clean up the text first. Look for speaker patterns and timestamps. Normalize formatting before analysis.

### Issue: No clear action items
**Solution:** Look for phrases like "will do", "I'll take care of", "let's follow up on", or task-oriented verbs (send, create, review, schedule).

### Issue: Multiple topics discussed simultaneously
**Solution:** Use timestamps to separate conversation threads. Group by topic rather than chronological order.

### Issue: Unclear ownership of action items
**Solution:** Flag items as "unassigned" and note that clarification is needed. List likely candidates based on discussion context.


### Markdown (Default)
Best for documentation, sharing via email, or saving as notes.

### JSON
Best for integration with other tools:
```json
{
  "meeting": {
    "title": "Project Kickoff",
    "date": "2025-11-12",
    "attendees": ["John", "Jane", "Bob"],
    "summary": "...",
    "decisions": [...],
    "actionItems": [
      {
        "task": "Create project plan",
        "owner": "John",
        "deadline": "2025-11-19"
      }
    ]
  }
}
```

### Email Format
Ready to send as a follow-up email with professional formatting.



## Notes

- Automated transcripts may contain errors - use context to interpret unclear sections
- Speaker identification may not be 100% accurate in large meetings
- Some Teams transcripts include chat messages - distinguish between spoken content and chat
- Be aware of confidential information when sharing summaries
