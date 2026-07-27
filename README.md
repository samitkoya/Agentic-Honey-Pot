# Agentic Honey-Pot

An AI-powered honeypot that pretends to be a gullible victim when scammers reach out. It keeps them talking, extracts useful intelligence like phone numbers, UPI IDs, bank accounts, and phishing links, and logs everything for analysis.

Built with FastAPI and Google Gemini.


## How It Works

When a scammer's message hits the API, three things happen in sequence:

1. **Scam Detection** -- Gemini analyzes the message and conversation history to determine if it is a scam, what kind, and how confident it is.
2. **Intelligence Extraction** -- Regex-based extractors pull out bank account numbers, UPI IDs, phone numbers, suspicious URLs, and known scam keywords from the raw text.
3. **Response Generation** -- Gemini generates a short, believable reply designed to sound like a confused, trusting person. The goal is to keep the scammer engaged long enough to reveal more information.

If Gemini is unavailable or the API key quota is exhausted, the system falls back to a rotating set of hardcoded prompts that ask for payment details, phone numbers, and links.


## Setup

**Prerequisites:** Python 3.10 or higher and a Google Gemini API key.

```bash
git clone https://github.com/samitkoya/Agentic-Honey-Pot.git
cd Agentic-Honey-Pot
```

Create a `.env` file from the template and fill in your keys:

```bash
cp .env.example .env
```

```
API_KEY=your-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
python main.py
```

The server starts at `http://localhost:8000`.


## API Reference

Every endpoint except `/` and `/health` requires an `X-API-Key` header.

### POST /api/honeypot

The main endpoint. Send a scammer's message and get back a convincing victim response.

**Request:**

```json
{
    "sessionId": "session-abc-123",
    "message": {
        "sender": "scammer",
        "text": "Your account is blocked. Send OTP to reactivate.",
        "timestamp": "2026-07-27T12:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}
```

- `sessionId` -- any unique string that ties messages in the same conversation together.
- `message.sender` -- either `"scammer"` or `"user"`.
- `message.timestamp` -- ISO-8601 string or epoch milliseconds.
- `conversationHistory` -- optional, previous messages for context on the first request.
- `metadata` -- optional, defaults to SMS / English / IN.

**Response:**

```json
{
    "status": "success",
    "reply": "Oh no, what do I do? Which number should I call to fix this?"
}
```

### GET /api/session/{sessionId}

Returns the full session state including extracted intelligence, scam detection results, and internal agent notes. Useful for debugging and reviewing what the system captured.

**Response:**

```json
{
    "session_id": "session-abc-123",
    "message_count": 4,
    "scam_detected": true,
    "scam_type": "bank_fraud",
    "confidence": 0.92,
    "intelligence": {
        "bankAccounts": ["1234567890123"],
        "upiIds": ["fraud@ybl"],
        "phishingLinks": ["https://fake-bank.xyz/verify"],
        "phoneNumbers": ["+919876543210"],
        "suspiciousKeywords": ["blocked", "otp", "verify"]
    },
    "agent_notes": [
        "Scam detected: bank_fraud (confidence: 0.92)",
        "Extracted: 1 accounts, 1 UPIs, 1 links, 1 phones"
    ]
}
```

### GET /api/rate-limit

Check how many requests you have left.

**Response:**

```json
{
    "limits": {
        "requests_per_minute": 10,
        "requests_per_day": 100
    },
    "remaining": {
        "remaining_per_minute": 9,
        "remaining_per_day": 98
    }
}
```

### GET /health

Returns `{"status": "healthy"}` if the server is running. No authentication required.


## Project Structure

```
Agentic-Honey-Pot/
├── main.py                          # FastAPI app, routes, rate limiter
├── app/
│   ├── agent.py                     # Gemini-powered response generation
│   ├── config.py                    # Environment variable loading
│   ├── intelligence_extractor.py    # Regex-based intel extraction
│   ├── models.py                    # Pydantic request/response models
│   ├── scam_detector.py             # Gemini-powered scam classification
│   └── session_manager.py           # In-memory session state
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```


## Rate Limits

Requests are throttled per API key:

- 10 requests per minute
- 100 requests per day

Exceeding either limit returns a `429` with a message indicating how long to wait.


## Errors

| Status | Meaning |
|--------|---------|
| 401 | Invalid or missing `X-API-Key` header |
| 422 | Malformed request body |
| 429 | Rate limit exceeded |


## License

MIT
