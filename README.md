# Agentic Honey-Pot API

An automated threat intelligence and counter-fraud honeypot system built with FastAPI and Google Gemini. The system pretends to be a vulnerable scam target to engage fraudsters in real-time dialog, extract actionable Cyber Threat Intelligence (CTI)—such as bank account numbers, UPI handles, phishing links, and phone numbers—and log intelligence output for security teams.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Key Capabilities](#key-capabilities)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Rate Limiting](#rate-limiting)
  - [Endpoints Summary](#endpoints-summary)
  - [POST /api/honeypot](#post-apihoneypot)
  - [GET /api/session/{session_id}](#get-apisessionsession_id)
  - [GET /api/rate-limit](#get-apirate-limit)
  - [GET /health](#get-health)
  - [GET /](#get-)
- [Intelligence Extraction Engine](#intelligence-extraction-engine)
- [Scam Detection & AI Agent Pipeline](#scam-detection--ai-agent-pipeline)
  - [Classifier Logic](#classifier-logic)
  - [Agent Persona & Strategy](#agent-persona--strategy)
  - [Fallback Mechanism](#fallback-mechanism)
- [Session Management & Data Persistence](#session-management--data-persistence)
- [Verification & End-to-End Testing](#verification--end-to-end-testing)
- [Project Layout](#project-layout)
- [Error Handling](#error-handling)

---

## System Architecture

The Agentic Honey-Pot operates as an asynchronous HTTP service. Incoming scam messages follow a deterministic multi-stage execution pipeline:

```
[ Incoming HTTP POST Request ]
              |
              v
[ Header Authentication (X-API-Key) ]
              |
              v
[ Rate Limiter (Memory Window Check) ]
              |
              v
[ Session State Initialization / Merge ]
              |
              v
[ Stage 1: Scam Detection (Gemini 3.1 Flash Lite) ]
              |
              v
[ Stage 2: Intelligence Extraction (Regex Parsing) ]
              |
              v
[ Stage 3: Honeypot Response Generation (Victim Roleplay) ]
              |
              v
[ Stage 4: File Persistence (Disk Logging) ]
              |
              v
[ JSON Response returned to API Client ]
```

---

## Key Capabilities

- **Automated Fraud Classification**: Uses Google Gemini (`gemini-3.1-flash-lite`) to analyze incoming conversational text, categorize fraud types (`bank_fraud`, `upi_fraud`, `phishing`, `fake_offer`), and score detection confidence from `0.0` to `1.0`.
- **Cyber Threat Intelligence (CTI) Parsing**: Evaluates text payloads against regular expressions to capture financial endpoints, payment routing addresses, malicious URLs, and Indian telecommunication formats.
- **Adaptive Persona Dialog**: Roleplays as a naive victim to keep malicious actors engaged without exposing detection status.
- **High-Availability Fallback**: Maintains uninterrupted operational status using a rotating fallback system of 15 human-crafted prompts if LLM quota is exhausted or API keys are unconfigured.
- **In-Memory Session Aggregation**: Merges incoming payload histories and tracks session metrics across multi-turn exchanges.
- **Disk-Based Intelligence Reporting**: Formats collected indicators into per-session files (`intelligence_logs/`) and a root summary report (`collected_intelligence.txt`).

---

## Prerequisites

- **Python**: Version 3.10 or higher.
- **API Access Key**: Custom client key for `X-API-Key` request header validation.
- **Google Gemini API Key**: Required for Gemini model inference (`gemini-3.1-flash-lite`). Fallback mode activates if omitted.

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/samitkoya/Agentic-Honey-Pot.git
cd Agentic-Honey-Pot
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the root directory by duplicating `.env.example`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS (Bash):**
```bash
cp .env.example .env
```

Set the values inside `.env`:

```env
# Authentication Key required in request headers
API_KEY=your-custom-secret-key

# Google Gemini API key for scam classification & response generation
GEMINI_API_KEY=your-google-gemini-api-key
```

If `GEMINI_API_KEY` is not provided, the API runs in fallback mode without breaking.

---

## Running the Application

### Development Server (with Auto-Reload)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment

Run directly via Uvicorn:

```bash
python main.py
```

Or run via Uvicorn CLI with multiple worker processes:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application starts listening at `http://localhost:8000`.

---

## API Reference

### Authentication

All endpoints under `/api/*` enforce header authentication via the `verify_api_key` dependency.

- **Header Name**: `X-API-Key`
- **Expected Value**: Matches the `API_KEY` configured in `.env`.
- **Unauthorized Behavior**: Returns `HTTP 401 Unauthorized` with body `{"detail": "Invalid API key"}`.

---

### Rate Limiting

Rate limiting is enforced per `X-API-Key` in memory:

- **Per Minute Limit**: 10 requests / 60 seconds window.
- **Per Day Limit**: 100 requests / 86,400 seconds window.
- **Exceeded Limit Behavior**: Returns `HTTP 429 Too Many Requests` with rate limit diagnostic text.

---

### Endpoints Summary

| HTTP Method | Path | Auth Required | Description |
|---|---|---|---|
| `GET` | `/` | No | API metadata and active operational state |
| `GET` | `/health` | No | Liveness and health check endpoint |
| `POST` | `/api/honeypot` | Yes (`X-API-Key`) | Primary ingestion endpoint for scam messages |
| `GET` | `/api/session/{session_id}` | Yes (`X-API-Key`) | Retrieves aggregated session state & intelligence |
| `GET` | `/api/rate-limit` | Yes (`X-API-Key`) | Checks current quota consumption and remaining allowances |

---

### POST /api/honeypot

Ingests incoming messages, updates session state, analyzes for scam indicators, extracts intelligence, generates an engaging response, and writes intelligence to disk.

#### Request Headers

```http
Content-Type: application/json
X-API-Key: your-custom-secret-key
```

#### Request Payload Schema (`HoneypotRequest`)

| Field | Type | Required | Description |
|---|---|---|---|
| `sessionId` | String | Yes | Unique conversation tracking ID |
| `message` | Object | Yes | Current message object (`sender`, `text`, `timestamp`) |
| `message.sender` | String | Yes | Sender label (`"scammer"` or `"user"`) |
| `message.text` | String | Yes | Message text string |
| `message.timestamp` | String / Integer | Yes | Timestamp string (ISO-8601) or epoch milliseconds |
| `conversationHistory` | Array | No | Optional list of prior `Message` objects |
| `metadata` | Object | No | Additional context attributes |

#### Request Payload Example

```json
{
  "sessionId": "session-109283",
  "message": {
    "sender": "scammer",
    "text": "ALERT: Your bank account is suspended. Transfer 1000 INR immediately to UPI target@okicici or call +919876543210 to unblock.",
    "timestamp": "2026-07-28T19:00:00Z"
  },
  "conversationHistory": []
}
```

#### Response Payload Schema (`HoneypotResponse`)

| Field | Type | Description |
|---|---|---|
| `status` | String | Operation status (`"success"` or `"error"`) |
| `reply` | String | Generated honeypot victim reply message |

#### Response Payload Example

```json
{
  "status": "success",
  "reply": "Oh no! Which bank account should I transfer to? Can you share the details?"
}
```

---

### GET /api/session/{session_id}

Retrieves current in-memory metadata, conversation history, audit notes, and threat intelligence aggregated for a given session.

#### Request Headers

```http
X-API-Key: your-custom-secret-key
```

#### Response Payload Example

```json
{
  "session_id": "session-109283",
  "message_count": 2,
  "scam_detected": true,
  "scam_type": "bank_fraud",
  "confidence": 0.95,
  "callback_sent": false,
  "intelligence": {
    "bankAccounts": [],
    "upiIds": ["target@okicici"],
    "phishingLinks": [],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["bank", "account", "transfer", "upi", "urgent"]
  },
  "agent_notes": [
    "Scam detected: bank_fraud (confidence: 0.95)",
    "Extracted: 0 accounts, 1 UPIs, 0 links, 1 phones",
    "Generated via Gemini | Scam type: bank_fraud"
  ]
}
```

---

### GET /api/rate-limit

Returns current capacity metrics for the provided API Key.

#### Request Headers

```http
X-API-Key: your-custom-secret-key
```

#### Response Payload Example

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

---

### GET /health

Liveness probe endpoint.

#### Response Example

```json
{
  "status": "healthy"
}
```

---

### GET /

Root metadata endpoint.

#### Response Example

```json
{
  "service": "Agentic Honey-Pot API",
  "version": "1.0.0",
  "status": "active"
}
```

---

## Intelligence Extraction Engine

Located in `app/intelligence_extractor.py`, the engine processes raw text using regular expressions to isolate technical indicators:

### Extraction Patterns

- **Bank Accounts**:
  - Regex: `\b\d{9,18}\b`
  - Validation: Filters strings under 10 digits or strings starting with `"20"`.
- **UPI Handles**:
  - Regex: `[a-zA-Z0-9._-]+@[a-zA-Z0-9]+`
  - Validation: Excludes standard email provider domains (`gmail`, `yahoo`, `hotmail`, `outlook`, `email`).
- **Phone Numbers**:
  - Regex: `(?:\+91[\-\s]?)?[789]\d{9}\b`
  - Sanitization: Strips space and hyphen characters; normalizes Indian 10-digit mobile numbers to `+91XXXXXXXXXX` standard format.
- **Phishing URLs**:
  - Regex: `https?://[^\s<>"\'{}|\\^`\[\]]+`
  - Validation: Inspects URLs against known suspicious indicators (`bit.ly`, `tinyurl`, `.xyz`, `.tk`, `verify`, `update`, `login`, `upi`, `payment`) and excludes trusted domains (`google.com`, `microsoft.com`, `apple.com`).
- **Suspicious Keywords**:
  - Matches text against a predefined lexicon (`lottery`, `prize`, `won`, `bank`, `account`, `otp`, `verify`, `kyc`, `upi`, `rbi`, `sbi`, `income tax`, `cashback`, etc.).

---

## Scam Detection & AI Agent Pipeline

### Classifier Logic

Implemented in `app/scam_detector.py`. The module accepts the current message text and trailing conversation history. It issues an asynchronous request to Gemini (`gemini-3.1-flash-lite`) using a structured prompt:

```text
Analyze this message for scam/fraud intent.

Previous conversation:
[Sender History]

Current message: [Message Text]

Respond in this exact format:
IS_SCAM: [yes/no]
CONFIDENCE: [0.0-1.0]
SCAM_TYPE: [bank_fraud/upi_fraud/phishing/fake_offer/unknown]
```

The output string is parsed to update the session's overall classification state when the detected confidence exceeds previously recorded values.

### Agent Persona & Strategy

Implemented in `app/agent.py`. The prompt configures Gemini to roleplay as an unsuspecting target. Operational rules enforced on the model:

1. Never reveal awareness of the scam.
2. Use natural, believable human phrasing.
3. Limit responses to 1-2 sentences (maximum 50 words / 200 characters).
4. Direct conversation flow toward requesting phone numbers, account numbers, payment links, and UPI IDs.
5. Project confusion, anxiety, or naivety.

### Fallback Mechanism

When `GEMINI_API_KEY` is omitted or API calls fail, `app/agent.py` uses a round-robin rotation over 15 predefined responses:

- *"Oh really? Can you tell me more? What number should I call you on?"*
- *"I'm interested! But I'm confused, can you send me the link again?"*
- *"Wait, which bank account should I transfer to? Can you share the details?"*
- *"I want to do this! What's your UPI ID so I can pay?"*
- *"Sorry, I didn't get that. Can you share your phone number? I'll call you."*

---

## Session Management & Data Persistence

Session state is handled in-memory by `app/session_manager.py` using a global state object `SESSIONS: Dict[str, SessionData]`.

### Data Lifecycle

1. **State Update**: incoming messages are appended to `conversation_history`.
2. **Intelligence Aggregation**: extracted indicators from new messages are merged with set operations to prevent duplicate entries.
3. **File Output**: Every message update triggers `save_intelligence_to_file()`, writing formatted output to two locations:
   - `intelligence_logs/extracted_intelligence_{session_id}.txt`
   - `collected_intelligence.txt` (root file containing the most recent session snapshot)

### Disk Report Format Example

```text
==================================================
          AGENTIC HONEY-POT REPORT                
==================================================
Session ID     : session-109283
Scam Detected  : True
Scam Type      : bank_fraud
Confidence     : 0.95
Message Count  : 2
--------------------------------------------------
EXTRACTED THREAT INTELLIGENCE:
  - Bank Accounts      : None
  - UPI IDs            : target@okicici
  - Phishing Links     : None
  - Phone Numbers      : +919876543210
  - Suspicious Keywords: bank, account, transfer, upi, urgent
--------------------------------------------------
CONVERSATION HISTORY:
  [SCAMMER]: ALERT: Your bank account is suspended. Transfer 1000 INR immediately to UPI target@okicici or call +919876543210 to unblock.
  [USER]: Oh no! Which bank account should I transfer to? Can you share the details?
--------------------------------------------------
AGENT NOTES:
  - Scam detected: bank_fraud (confidence: 0.95)
  - Extracted: 0 accounts, 1 UPIs, 0 links, 1 phones
  - Generated via Gemini | Scam type: bank_fraud
==================================================
```

---

## Verification & End-to-End Testing

### 1. Verify Service Liveness

```bash
curl -X GET "http://localhost:8000/health"
```

### 2. Execute Ingestion Flow via `curl`

```bash
curl -X POST "http://localhost:8000/api/honeypot" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: default-secret-key" \
     -d '{
       "sessionId": "test-session-001",
       "message": {
         "sender": "scammer",
         "text": "Your electricity connection will be disconnected tonight! Pay bill to UPI billpay@okaxis or call 9876543210",
         "timestamp": 1770000000
       }
     }'
```

### 3. Verify via Python Client Script

Save as `test_client.py`:

```python
import requests

API_URL = "http://localhost:8000/api/honeypot"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "default-secret-key"
}

payload = {
    "sessionId": "py-session-404",
    "message": {
        "sender": "scammer",
        "text": "You have won a lottery of 50,000 INR! Verify account details at https://secure-lottery-claim.xyz/login or send details to scammer@ybl",
        "timestamp": "2026-07-28T19:15:00Z"
    }
}

response = requests.post(API_URL, json=payload, headers=HEADERS)
print("HTTP Status Code:", response.status_code)
print("Response JSON:", response.json())
```

Run test:

```bash
python test_client.py
```

### 4. Verify Session Aggregation

```bash
curl -X GET "http://localhost:8000/api/session/py-session-404" \
     -H "X-API-Key: default-secret-key"
```

---

## Project Layout

```
Agentic-Honey-Pot/
│
├── main.py                       # FastAPI initialization, routing, rate limiting, and dependencies
├── requirements.txt              # System dependencies
├── .env.example                  # Environment configuration template
├── README.md                     # Technical reference & operational documentation
├── collected_intelligence.txt    # Latest written intelligence report snapshot
│
├── app/
│   ├── __init__.py               # Module identifier
│   ├── agent.py                  # Gemini response generation & fallback prompt engine
│   ├── config.py                 # Environment parsing & scam keyword vocabulary
│   ├── intelligence_extractor.py # Regex extraction logic for CTI artifacts
│   ├── models.py                 # Pydantic data schemas for API requests & sessions
│   ├── scam_detector.py          # Gemini fraud classifier & confidence evaluator
│   └── session_manager.py        # In-memory session tracking & disk file logging
│
└── intelligence_logs/            # Generated per-session intelligence text reports
    └── extracted_intelligence_*.txt
```

---

## Error Handling

| HTTP Code | Exception Cause | Mitigation |
|---|---|---|
| `401 Unauthorized` | Missing or invalid `X-API-Key` header | Provide matching key configured in `.env` |
| `429 Too Many Requests` | Exceeded 10 req/min or 100 req/day threshold | Delay requests until sliding window clears |
| `422 Unprocessable Entity` | Malformed JSON schema or missing required fields | Check request structure against `HoneypotRequest` model |
| `500 Internal Server Error` | Unhandled exception during processing | Check server application output logs |

---

## License

MIT License.
