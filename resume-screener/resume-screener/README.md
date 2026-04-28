# RecruitIQ — Resume Screener

AI-powered resume screening that ranks candidates against a job description.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# macOS / Linux
export ANTHROPIC_API_KEY=your_api_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

Get your API key at: https://console.anthropic.com/

### 3. Run the server
```bash
python app.py
```

### 4. Open the app
Visit http://localhost:5000 in your browser.

---

## How to use

1. **Paste a job description** in the left panel
2. **Upload resumes** (PDF or .txt, up to 10 files)
3. Click **Analyze & rank candidates**
4. Click any candidate card to see the full breakdown

## Features

- PDF text extraction
- Multi-dimensional scoring: Technical, Experience, Education, Culture Fit
- Matched & missing skills per candidate
- Bias detection flags
- Recruiter insight summary
