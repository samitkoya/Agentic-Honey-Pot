# API Usage Guide

This guide explains how to use the Agentic Honey-Pot API when running locally.

## Step 1: Start the Server

Open a terminal and run:

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The server is now running at: `http://localhost:8000`

## Step 2: Test the Server

Open a browser and go to: `http://localhost:8000`

Expected Output:
```json
{
    "service": "Agentic Honey-Pot API",
    "version": "1.0.0",
    "status": "active"
}
```

## Step 3: Using the Honeypot API

**Endpoint:** `POST http://localhost:8000/api/honeypot`

**Required Headers:**
- `X-API-Key`: your-api-key (from .env file)
- `Content-Type`: application/json

### Input Format

```json
{
    "sessionId": "unique-session-id",
    "message": {
        "sender": "scammer",
        "text": "The scammer's message text here",
        "timestamp": "2026-02-07T12:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}
```

**Field Descriptions:**
| Field | Required | Description |
|-------|----------|-------------|
| sessionId | Yes | Unique ID to track conversation. Use same ID for multi-turn chats |
| message | Yes | The current message from the scammer |
| message.sender | Yes | Always "scammer" for incoming messages |
| message.text | Yes | The actual message content |
| message.timestamp | Yes | ISO format timestamp or Unix milliseconds |
| conversationHistory | No | Array of previous messages in the session |
| metadata | No | Additional context about the message source |

### Output Format

**Success Response (200 OK):**
```json
{
    "status": "success",
    "reply": "Oh really? What number should I call you on?"
}
```

**Field Descriptions:**
| Field | Description |
|-------|-------------|
| status | "success" if processed correctly |
| reply | The AI-generated response to engage the scammer |

**Error Responses:**
| Code | Meaning |
|------|---------|
| 401 | Invalid or missing API key |
| 422 | Invalid request format |
| 429 | Rate limit exceeded |

## Example Requests

### Using PowerShell

```powershell
$headers = @{
    "X-API-Key" = "use1029384yours"
    "Content-Type" = "application/json"
}

$body = @{
    sessionId = "test-001"
    message = @{
        sender = "scammer"
        text = "Congratulations! You won Rs 50 lakh lottery. Send OTP to claim."
        timestamp = "2026-02-07T12:00:00Z"
    }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8000/api/honeypot" -Method Post -Headers $headers -Body $body
```

### Using curl

```bash
curl -X POST http://localhost:8000/api/honeypot \
  -H "Content-Type: application/json" \
  -H "X-API-Key: use1029384yours" \
  -d '{"sessionId": "test-001", "message": {"sender": "scammer", "text": "You won a lottery!", "timestamp": "2026-02-07T12:00:00Z"}}'
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/honeypot"
headers = {
    "X-API-Key": "use1029384yours",
    "Content-Type": "application/json"
}
data = {
    "sessionId": "test-001",
    "message": {
        "sender": "scammer",
        "text": "Your bank account is blocked. Click here to verify.",
        "timestamp": "2026-02-07T12:00:00Z"
    }
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Multi-Turn Conversation Example

**Turn 1 - Scammer sends first message:**

Input:
```json
{
    "sessionId": "scam-session-123",
    "message": {
        "sender": "scammer",
        "text": "Your SBI account is blocked. Call immediately.",
        "timestamp": "2026-02-07T12:00:00Z"
    }
}
```

Output:
```json
{
    "status": "success",
    "reply": "What? My account is blocked? How can that be?"
}
```

**Turn 2 - Scammer responds:**

Input:
```json
{
    "sessionId": "scam-session-123",
    "message": {
        "sender": "scammer",
        "text": "Yes sir, you need to verify your details. What is your account number?",
        "timestamp": "2026-02-07T12:01:00Z"
    }
}
```

Output:
```json
{
    "status": "success",
    "reply": "Oh no! But which branch should I call? What's your number?"
}
```

> **Note:** Same sessionId maintains conversation context

## Other Endpoints

### Health Check

```
GET http://localhost:8000/health
```

Output:
```json
{
    "status": "healthy"
}
```

### Get Session Info

```
GET http://localhost:8000/api/session/{sessionId}
Header: X-API-Key: your-api-key
```

Output:
```json
{
    "session_id": "test-001",
    "message_count": 4,
    "scam_detected": true,
    "scam_type": "bank_fraud",
    "confidence": 0.85,
    "callback_sent": false,
    "intelligence": {
        "bankAccounts": [],
        "upiIds": ["scammer@upi"],
        "phishingLinks": ["http://fake-bank.com"],
        "phoneNumbers": ["9876543210"]
    },
    "agent_notes": [...]
}
```

### Rate Limit Status

```
GET http://localhost:8000/api/rate-limit
Header: X-API-Key: your-api-key
```

Output:
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

## Common Errors & Solutions

| Error | Solution |
|-------|----------|
| "Invalid API key" | Check X-API-Key header matches API_KEY in .env file |
| "Empty request body" | Make sure you're sending JSON in the request body |
| "Validation failed" | Check that sessionId and message fields are present |
| "Rate limit exceeded" | Wait for cooldown period (1 min or 24 hours) |
