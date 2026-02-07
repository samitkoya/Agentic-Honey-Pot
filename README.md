# 🍯 Agentic Honey-Pot

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

### Request

```bash
curl -X POST http://localhost:8000/api/honeypot \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "sessionId": "session-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account is blocked. Click here to verify.",
      "timestamp": "2026-02-07T12:00:00Z"
    }
  }'
```

### Response

```json
{
  "status": "success",
  "reply": "What? My account is blocked? How can that be?"
}
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
