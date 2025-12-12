# Meeting Summary Agent

Transform meeting transcripts into actionable summaries with AI.

## Features

- Paste any meeting transcript
- Get instant TL;DR summary
- Extract action items with owners and deadlines
- Identify key decisions
- Surface open questions
- Copy or download results

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
2. Click "Summarize Meeting"
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
