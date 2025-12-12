# Meeting Summary Agent - Implementation Specification

## Overview

Build a web application that allows users to paste meeting transcripts and receive structured summaries with action items and TL;DRs. The app should be simple, clean, and deployable to Streamlit Cloud.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Streamlit |
| AI Backend | Langbase REST API |
| Language | Python 3.10+ |
| Hosting | Streamlit Cloud |

---

## Project Structure

```
meeting-summary-app/
├── app.py                    # Main Streamlit application
├── langbase_client.py        # Langbase API client
├── prompts.py                # System prompts for summarization
├── utils.py                  # Helper functions
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── .env.example              # Environment variables template
├── sample_transcript.txt     # Sample transcript for testing
└── README.md                 # Setup and deployment guide
```

---

## File Specifications

### 1. `requirements.txt`

```
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

### 2. `prompts.py`

Create a system prompt that instructs the LLM to analyze meeting transcripts and return structured JSON.

**System Prompt Requirements:**
- Role: Expert meeting analyst
- Task: Extract key information from transcripts
- Output: Strictly valid JSON

**Required JSON Output Schema:**

```json
{
  "tldr": "2-3 sentence executive summary",
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
```

**Prompt Guidelines:**
- If no action items are found, return empty array
- Infer priority based on urgency language (ASAP = high, when possible = low)
- Extract deadlines in readable format (e.g., "December 15", "Next Monday")
- If owner is unclear, set to null
- Keep TL;DR under 50 words

---

### 3. `langbase_client.py`

Create a client class to interact with Langbase REST API.

**Langbase API Details:**

- **Endpoint:** `https://api.langbase.com/v1/pipes/run`
- **Method:** POST
- **Headers:**
  ```
  Authorization: Bearer <LANGBASE_API_KEY>
  Content-Type: application/json
  ```

**Request Body Structure:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "<system_prompt>"
    },
    {
      "role": "user", 
      "content": "<transcript>"
    }
  ],
  "model": "openai:gpt-4o",
  "stream": false
}
```

**Alternative: Create Pipe First**

If using a pre-created pipe, the endpoint becomes:
```
POST https://api.langbase.com/v1/pipes/run
```

With body:
```json
{
  "name": "meeting-summary-agent",
  "messages": [
    {
      "role": "user",
      "content": "<transcript>"
    }
  ],
  "stream": false
}
```

**Client Class Requirements:**

```python
class LangbaseClient:
    def __init__(self, api_key: str):
        """Initialize with API key"""
        
    def summarize_meeting(self, transcript: str) -> dict:
        """
        Send transcript to Langbase and return parsed summary.
        
        Args:
            transcript: Raw meeting transcript text
            
        Returns:
            Parsed JSON summary dict
            
        Raises:
            Exception on API errors
        """
```

**Error Handling:**
- Handle network timeouts (set timeout to 60s for long transcripts)
- Handle API errors (non-200 responses)
- Handle JSON parsing errors from LLM response
- Return user-friendly error messages

---

### 4. `utils.py`

Helper functions for formatting and export.

**Required Functions:**

```python
def format_summary_markdown(summary: dict) -> str:
    """
    Convert summary dict to formatted markdown string.
    Used for copy/download functionality.
    """

def validate_transcript(text: str) -> tuple[bool, str]:
    """
    Basic validation of transcript input.
    Returns (is_valid, error_message)
    
    Checks:
    - Not empty
    - Minimum length (at least 100 characters)
    - Maximum length (warn if > 50,000 characters)
    """

def estimate_tokens(text: str) -> int:
    """
    Rough token estimate (chars / 4).
    Used to warn users about very long transcripts.
    """
```

---

### 5. `app.py`

Main Streamlit application.

**Page Configuration:**
```python
st.set_page_config(
    page_title="Meeting Summary Agent",
    page_icon="📋",
    layout="wide"
)
```

**UI Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  📋 Meeting Summary Agent                                   │
│  Transform meeting transcripts into actionable summaries    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Left Column - 50%]          [Right Column - 50%]          │
│  ┌─────────────────────┐      ┌─────────────────────┐       │
│  │ Paste your meeting  │      │ Summary appears     │       │
│  │ transcript here...  │      │ here after          │       │
│  │                     │      │ processing...       │       │
│  │                     │      │                     │       │
│  │ (text_area)         │      │ (results)           │       │
│  │                     │      │                     │       │
│  └─────────────────────┘      └─────────────────────┘       │
│                                                             │
│  [✨ Summarize Meeting]                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Results Display (Right Column):**

When summary is ready, display:

1. **TL;DR Section**
   - Blue info box with executive summary

2. **Action Items Table**
   - Columns: Task | Owner | Deadline | Priority
   - Priority shown as colored badges (🔴 High, 🟡 Medium, 🟢 Low)
   - Show "No action items found" if empty

3. **Key Decisions**
   - Bulleted list with decision + context

4. **Key Topics**
   - Simple bulleted list

5. **Open Questions**
   - Warning-styled list (yellow background)

6. **Next Steps**
   - Numbered list

7. **Export Buttons**
   - "📋 Copy to Clipboard" - copies markdown version
   - "⬇️ Download as Markdown" - downloads .md file

**State Management:**
- Use `st.session_state` to persist summary between reruns
- Clear previous summary when new transcript is submitted

**Loading State:**
- Show spinner with "Analyzing transcript..." message
- Disable button while processing

**Error Handling:**
- Display errors in red error box
- Show helpful messages (e.g., "Transcript too short", "API error - try again")

---

### 6. `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 10
```

---

### 7. `.env.example`

```
# Get your API key from: https://langbase.com/settings/api-keys
LANGBASE_API_KEY=your_api_key_here
```

---

### 8. `sample_transcript.txt`

Create a realistic sample transcript for testing:

```
Meeting: Q4 Planning Session
Date: December 10, 2024
Attendees: Sarah (PM), John (Engineering Lead), Mike (Design), Lisa (Marketing)

Sarah: Good morning everyone. Let's discuss our Q4 priorities and get aligned on the roadmap.

John: Thanks Sarah. From engineering, we have three major items. First, the API v2 migration needs to be completed by end of January. Second, we need to address the performance issues reported by enterprise customers.

Sarah: What's the timeline looking like for the performance fixes?

John: I'd estimate two weeks once we start. We should prioritize this - it's affecting our largest accounts.

Mike: On the design side, we've finalized the new dashboard mockups. I'll share the Figma links after this call. We need engineering review before we proceed.

Sarah: John, can your team review Mike's designs by Friday?

John: Yes, I'll assign that to the frontend team. Let's say end of day Friday.

Lisa: For marketing, we're planning the January product launch announcement. I need final feature list from John by December 20th to prepare materials.

John: Noted. I'll have that ready.

Sarah: Great. Let's also discuss the budget. We have approval for two additional contractors. John, do you have candidates in mind?

John: Yes, I've been talking to two senior developers. I'll send their profiles to HR today.

Mike: One question - are we still planning to sunset the old dashboard in Q1?

Sarah: Good question. Let's defer that decision until we see adoption metrics for the new dashboard. We'll revisit in our January planning.

Sarah: Alright, to summarize the key actions: John reviews designs by Friday, John sends feature list to Lisa by Dec 20, John sends contractor profiles to HR today. Anything else?

Lisa: I'll schedule a follow-up with John for the launch content review.

Sarah: Perfect. Thanks everyone. Let's reconvene next Tuesday.
```

---

### 9. `README.md`

Create comprehensive documentation:

```markdown
# 📋 Meeting Summary Agent

Transform meeting transcripts into actionable summaries with AI.

## Features

- ✨ Paste any meeting transcript
- 📝 Get instant TL;DR summary
- ✅ Extract action items with owners and deadlines
- 📌 Identify key decisions
- ❓ Surface open questions
- 📋 Copy or download results

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Langbase API key ([Get one here](https://langbase.com))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/meeting-summary-app.git
   cd meeting-summary-app
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your LANGBASE_API_KEY
   ```

5. Run the app:
   ```bash
   streamlit run app.py
   ```

6. Open http://localhost:8501 in your browser

## Deployment to Streamlit Cloud

### Step 1: Push to GitHub

Push this code to a GitHub repository.

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`

### Step 3: Add Secrets

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets"
3. Add your secrets in TOML format:
   ```toml
   LANGBASE_API_KEY = "your_api_key_here"
   ```

### Step 4: Deploy

Click "Deploy" and wait for the build to complete.

Your app will be available at: `https://your-app-name.streamlit.app`

## Usage

1. Paste your meeting transcript in the left text area
2. Click "✨ Summarize Meeting"
3. View the structured summary on the right
4. Copy to clipboard or download as Markdown

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LANGBASE_API_KEY` | Your Langbase API key |

## Tech Stack

- [Streamlit](https://streamlit.io/) - Web framework
- [Langbase](https://langbase.com/) - AI backend
- [GPT-4o](https://openai.com/) - Language model (via Langbase)

## License

MIT
```

---

## Implementation Notes

### API Key Handling

In Streamlit, access secrets like this:

```python
import os
import streamlit as st

# Try Streamlit secrets first (for cloud deployment)
# Fall back to environment variable (for local development)
api_key = st.secrets.get("LANGBASE_API_KEY") or os.getenv("LANGBASE_API_KEY")
```

### Handling Long Transcripts

- Warn users if transcript > 30,000 characters
- Set appropriate timeout (60-90 seconds)
- Consider chunking for very long transcripts (future enhancement)

### JSON Parsing

The LLM response may include markdown code blocks. Strip them:

```python
def parse_llm_json(response_text: str) -> dict:
    # Remove markdown code blocks if present
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())
```

### Copy to Clipboard

Streamlit doesn't have native clipboard support. Use this workaround:

```python
import streamlit.components.v1 as components

def copy_to_clipboard(text: str):
    components.html(
        f"""
        <script>
        navigator.clipboard.writeText(`{text}`);
        </script>
        """,
        height=0
    )
```

Or simply provide a text area with the markdown for manual copying.

---

## Testing Checklist

- [ ] Empty transcript shows validation error
- [ ] Very short transcript shows warning
- [ ] Sample transcript processes successfully
- [ ] All summary sections display correctly
- [ ] Action items table renders properly
- [ ] Download button produces valid markdown file
- [ ] Error states display user-friendly messages
- [ ] App works on mobile viewport
- [ ] Secrets load correctly in Streamlit Cloud

---

## Future Enhancements (Out of Scope for V1)

- Meeting type detection (standup, planning, etc.)
- Multiple language support
- Transcript file upload (.txt, .vtt)
- Integration with calendar/meeting apps
- Summary history/storage
- Team sharing features