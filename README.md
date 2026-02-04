# Agentic Honey-Pot System

An AI-powered honeypot REST API that detects scam messages, engages scammers in multi-turn conversations, extracts intelligence, and reports results to GUVI's evaluation endpoint.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "c:\Users\Samit Reddy\Desktop\AIHP\Agentic-Honey-Pot"
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your API keys:

```bash
copy .env.example .env
```

Edit `.env` with your values:
```env
API_KEY=your-secret-api-key
GEMINI_API_KEY=your-gemini-api-key
LLM_PROVIDER=gemini
ENGAGEMENT_THRESHOLD=5
```

### 3. Run the Server

```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Main Honeypot Endpoint
```
POST /api/honeypot
Header: x-api-key: YOUR_SECRET_KEY
Content-Type: application/json
```

**Request Body (First Message):**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-31T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "What? My account is blocked? How can that be?"
}
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Incoming Request                      │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│                  API Key Validation                      │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   Scam Detection                         │
│  • Keyword Analysis    • Pattern Matching    • LLM       │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   AI Agent Response                      |
│  • Persona Selection   • Tactic Selection    • Response  |
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│               Intelligence Extraction                    │
│  • Bank Accounts  • UPI IDs  • Links  • Phone Numbers    │
└────────────────────────┬─────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│                GUVI Callback (when ready)                │
└──────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
AIHP/
├── main.py                 # FastAPI application
├── config.py               # Configuration & constants
├── models.py               # Pydantic data models
├── scam_detector.py        # Scam detection engine
├── agent.py                # AI agent for engagement
├── intelligence_extractor.py # Intelligence extraction
├── session_manager.py      # Session management
├── guvi_callback.py        # GUVI API callback
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔑 Features

- **Hybrid Scam Detection**: Keyword matching + LLM classification
- **Multi-Persona Agent**: Confused elderly, naive user, busy professional
- **Engagement Tactics**: Clarification, delays, verification requests
- **Intelligence Extraction**: Bank accounts, UPI IDs, phone numbers, URLs
- **Session Management**: Tracks multi-turn conversations
- **GUVI Integration**: Automatic callback when engagement threshold reached

## 🧪 Testing

```powershell
# Test with PowerShell
$headers = @{
    "x-api-key" = "your-api-key"
    "Content-Type" = "application/json"
}
$body = @{
    sessionId = "test-001"
    message = @{
        sender = "scammer"
        text = "Your bank account will be blocked. Click here: http://fake.link/verify"
        timestamp = "2026-01-31T10:00:00Z"
    }
    conversationHistory = @()
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8000/api/honeypot" -Method Post -Headers $headers -Body $body
```

## 📝 License

MIT License - Built for GUVI Hackathon 2026
