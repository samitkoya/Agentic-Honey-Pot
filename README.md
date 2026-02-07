# Agentic Honey-Pot

AI-powered honeypot REST API that detects scam messages, engages scammers in conversations, and extracts intelligence.

## Features

- **Scam Detection** - Keyword analysis + LLM-based classification
- **AI Agent** - Engages scammers using Gemini 1.5 Flash with smart fallback responses
- **Intelligence Extraction** - Captures bank accounts, UPI IDs, phone numbers, and phishing links
- **Session Management** - Tracks multi-turn conversations
- **Rate Limiting** - 10 RPM, 100 RPD protection

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
API_KEY=your-secret-api-key
GEMINI_API_KEY=your-gemini-api-key
ENGAGEMENT_THRESHOLD=10
```

### 3. Run the Server

```bash
python main.py
```

Server runs at `http://localhost:8000`

### 4. Expose Publicly (Optional)

See [NGROK_SETUP.txt](NGROK_SETUP.txt) for detailed deployment instructions.

```bash
ngrok http 8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/honeypot` | POST | Main honeypot endpoint |
| `/api/session/{id}` | GET | Get session info |
| `/api/rate-limit` | GET | Rate limit status |

## Usage

📖 **For complete examples, see [API_USAGE_GUIDE.txt](API_USAGE_GUIDE.txt)**

### Input Format

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "The scammer's message",
    "timestamp": "2026-02-07T12:00:00Z"
  }
}
```

### Output Format

```json
{
  "status": "success",
  "reply": "AI-generated response to engage scammer"
}
```

### Quick Test (PowerShell)

```powershell
$headers = @{ "X-API-Key" = "your-api-key"; "Content-Type" = "application/json" }
$body = '{"sessionId": "test", "message": {"sender": "scammer", "text": "You won lottery!", "timestamp": "2026-02-07T12:00:00Z"}}'
Invoke-RestMethod -Uri "http://localhost:8000/api/honeypot" -Method Post -Headers $headers -Body $body
```

## Project Structure

```
Agentic-Honey-Pot/
├── app/
│   ├── __init__.py              # Package init
│   ├── agent.py                 # AI agent (Gemini + fallbacks)
│   ├── config.py                # Configuration
│   ├── intelligence_extractor.py # Extracts scammer details
│   ├── models.py                # Pydantic models
│   ├── scam_detector.py         # Scam detection engine
│   └── session_manager.py       # Session tracking
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
├── .env                         # Environment variables
├── NGROK_SETUP.txt              # ngrok deployment guide
├── API_USAGE_GUIDE.txt          # Input/output reference
└── README.md
```

## Architecture

```
Request → API Key Validation → Rate Limiting → Scam Detection
                                                    ↓
                                            AI Agent Response
                                                    ↓
                                        Intelligence Extraction
                                                    ↓
                                              Response
```

## Fallback Responses

When LLM is unavailable, the system uses 15 rotating prompts designed to extract scammer details:
- Phone numbers
- Bank account details
- UPI IDs
- Phishing links
