import time
from typing import Dict
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.models import HoneypotRequest, HoneypotResponse, Message
from app.config import API_KEY
from app.scam_detector import detect_scam
from app.agent import generate_response
from app.intelligence_extractor import extract_intelligence
from app import session_manager

REQUESTS_PER_MINUTE = 10
REQUESTS_PER_DAY = 100
_req_history: Dict[str, list] = defaultdict(list)


def _cleanup_reqs(key: str, now: float):
    _req_history[key] = [ts for ts in _req_history[key] if now - ts < 86400]


def check_rate_limit_key(key: str) -> tuple[bool, str]:
    now = time.time()
    _cleanup_reqs(key, now)
    recent = _req_history[key]
    min_count = sum(1 for ts in recent if now - ts < 60)
    if min_count >= REQUESTS_PER_MINUTE:
        return False, "Rate limit exceeded: 10 requests per minute limit reached."
    if len(recent) >= REQUESTS_PER_DAY:
        return False, "Rate limit exceeded: 100 requests per day limit reached."
    return True, ""


def record_request(key: str):
    _req_history[key].append(time.time())


def get_remaining_requests(key: str) -> dict:
    now = time.time()
    _cleanup_reqs(key, now)
    recent = _req_history[key]
    min_count = sum(1 for ts in recent if now - ts < 60)
    return {
        "remaining_per_minute": max(0, REQUESTS_PER_MINUTE - min_count),
        "remaining_per_day": max(0, REQUESTS_PER_DAY - len(recent))
    }


app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


async def check_rate_limit(x_api_key: str = Header(...)):
    allowed, error_msg = check_rate_limit_key(x_api_key)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    return x_api_key


@app.get("/")
async def root():
    return {
        "service": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    api_key: str = Depends(verify_api_key),
    _rate_check: str = Depends(check_rate_limit)
):
    record_request(api_key)
    
    session_id = request.sessionId
    current_message = request.message
    history = request.conversationHistory or []
    
    session = session_manager.get_session(session_id)
    session_manager.add_message(session_id, current_message)
    
    if history and len(session.conversation_history) <= 1:
        for msg in history:
            if msg not in session.conversation_history:
                session_manager.add_message(session_id, msg)
    
    is_scam, confidence, scam_type = await detect_scam(
        current_message.text,
        session.conversation_history
    )
    
    if is_scam and confidence > session.confidence:
        session_manager.update_session(
            session_id,
            scam_detected=True,
            scam_type=scam_type,
            confidence=confidence
        )
        session_manager.add_agent_note(
            session_id,
            f"Scam detected: {scam_type} (confidence: {confidence:.2f})"
        )
    
    intel = extract_intelligence(current_message.text)
    session_manager.update_intelligence(session_id, intel)
    
    if any([intel.bankAccounts, intel.upiIds, intel.phishingLinks, intel.phoneNumbers]):
        session_manager.add_agent_note(
            session_id,
            f"Extracted: {len(intel.bankAccounts)} accounts, {len(intel.upiIds)} UPIs, "
            f"{len(intel.phishingLinks)} links, {len(intel.phoneNumbers)} phones"
        )
    
    reply, agent_note = await generate_response(
        current_message.text,
        session.conversation_history,
        session.scam_type or scam_type or "unknown",
        session.message_count
    )
    session_manager.add_agent_note(session_id, agent_note)
    
    agent_message = Message(
        sender="user",
        text=reply,
        timestamp=current_message.timestamp
    )
    session_manager.add_message(session_id, agent_message)
    session_manager.save_intelligence_to_file(session_id)
    
    return HoneypotResponse(
        status="success",
        reply=reply
    )


@app.get("/api/session/{session_id}")
async def get_session_info(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    session = session_manager.get_session(session_id)
    return {
        "session_id": session.session_id,
        "message_count": session.message_count,
        "scam_detected": session.scam_detected,
        "scam_type": session.scam_type,
        "confidence": session.confidence,
        "callback_sent": session.callback_sent,
        "intelligence": session.intelligence.model_dump(),
        "agent_notes": session.agent_notes
    }


@app.get("/api/rate-limit")
async def get_rate_limit_status(
    api_key: str = Depends(verify_api_key)
    x_api_key: str = Header(None)
):
    if not x_api_key:
        return {
            "limits": {
                "requests_per_minute": REQUESTS_PER_MINUTE,
                "requests_per_day": REQUESTS_PER_DAY
            },
            "remaining": "Provide x-api-key header to view remaining requests."
        }
        
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    return {
        "limits": {
            "requests_per_minute": REQUESTS_PER_MINUTE,
            "requests_per_day": REQUESTS_PER_DAY
        },
        "remaining": get_remaining_requests(api_key)
        "remaining": get_remaining_requests(x_api_key)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
