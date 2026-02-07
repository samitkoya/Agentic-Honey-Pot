"""
Agentic Honey-Pot System - Main FastAPI Application

An AI-powered honeypot REST API that detects scam messages, 
engages scammers in multi-turn conversations, and extracts intelligence.
"""

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import time
import json

from app.models import HoneypotRequest, HoneypotResponse, Message
from app.config import API_KEY
from app.scam_detector import scam_detector
from app.agent import honeypot_agent
from app.intelligence_extractor import intelligence_extractor
from app.session_manager import session_manager


# ========== RATE LIMITING ==========
# Rate limits: 10 requests per day (RPD), 1 request per minute (RPM)
REQUESTS_PER_DAY = 100
REQUESTS_PER_MINUTE = 10

class RateLimiter:
    """In-memory rate limiter with RPD and RPM limits."""
    
    def __init__(self):
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.daily_requests: Dict[str, list] = defaultdict(list)
    
    def _cleanup_old_requests(self, key: str):
        """Remove expired timestamps."""
        now = time.time()
        # Clean minute requests (older than 60 seconds)
        self.minute_requests[key] = [
            ts for ts in self.minute_requests[key] if now - ts < 60
        ]
        # Clean daily requests (older than 24 hours)
        self.daily_requests[key] = [
            ts for ts in self.daily_requests[key] if now - ts < 86400
        ]
    
    def check_rate_limit(self, key: str) -> tuple[bool, str]:
        """
        Check if request is allowed.
        Returns (allowed, error_message)
        """
        self._cleanup_old_requests(key)
        now = time.time()
        
        # Check RPM (1 request per minute)
        if len(self.minute_requests[key]) >= REQUESTS_PER_MINUTE:
            wait_time = 60 - (now - self.minute_requests[key][0])
            return False, f"Rate limit exceeded: 1 request per minute. Wait {int(wait_time)} seconds."
        
        # Check RPD (10 requests per day)
        if len(self.daily_requests[key]) >= REQUESTS_PER_DAY:
            oldest = self.daily_requests[key][0]
            wait_time = 86400 - (now - oldest)
            hours = int(wait_time // 3600)
            minutes = int((wait_time % 3600) // 60)
            return False, f"Rate limit exceeded: 10 requests per day. Wait {hours}h {minutes}m."
        
        return True, ""
    
    def record_request(self, key: str):
        """Record a successful request."""
        now = time.time()
        self.minute_requests[key].append(now)
        self.daily_requests[key].append(now)
    
    def get_remaining(self, key: str) -> dict:
        """Get remaining requests."""
        self._cleanup_old_requests(key)
        return {
            "remaining_per_minute": REQUESTS_PER_MINUTE - len(self.minute_requests[key]),
            "remaining_per_day": REQUESTS_PER_DAY - len(self.daily_requests[key])
        }

# Global rate limiter instance
rate_limiter = RateLimiter()


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key authentication."""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return x_api_key


async def check_rate_limit(x_api_key: str = Header(...)):
    """Check rate limits for the API key."""
    allowed, error_msg = rate_limiter.check_rate_limit(x_api_key)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=error_msg
        )
    return x_api_key


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    raw_request: Request,
    api_key: str = Depends(verify_api_key),
    _rate_check: str = Depends(check_rate_limit)
):
    """
    Main honeypot endpoint
    Handles manual body parsing to allow missing Content-Type headers
    """
    # =========================================================================
    # ROBUST BODY PARSING START
    # =========================================================================
    try:
        # Read raw body bytes
        body_bytes = await raw_request.body()
        if not body_bytes:
            raise HTTPException(status_code=400, detail="Empty request body")
            
        # Manually parse JSON
        try:
            body_data = json.loads(body_bytes)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
            
        # Validate against Pydantic model
        request = HoneypotRequest(**body_data)
        
    except ValueError as e:
        # Pydantic validation error
        raise HTTPException(status_code=422, detail=f"Validation failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")
    # =========================================================================
    # ROBUST BODY PARSING END
    # =========================================================================
    
    # Record this request for rate limiting
    rate_limiter.record_request(api_key)
    
    session_id = request.sessionId
    current_message = request.message
    history = request.conversationHistory or []
    
    # Get or create session
    session = session_manager.get_session(session_id)
    
    # Add incoming message to session
    session_manager.add_message(session_id, current_message)
    
    # Also add any history that's not already tracked
    if history and len(session.conversation_history) <= 1:
        for msg in history:
            if msg not in session.conversation_history:
                session_manager.add_message(session_id, msg)
    
    # Step 1: Detect scam intent
    is_scam, confidence, scam_type = await scam_detector.detect(
        current_message.text,
        session.conversation_history
    )
    
    # Update session with scam detection results
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
    
    # Step 2: Extract intelligence from current message
    intel = intelligence_extractor.extract_from_text(current_message.text)
    session_manager.update_intelligence(session_id, intel)
    
    # Log extracted intelligence
    if any([intel.bankAccounts, intel.upiIds, intel.phishingLinks, intel.phoneNumbers]):
        session_manager.add_agent_note(
            session_id,
            f"Extracted: {len(intel.bankAccounts)} accounts, {len(intel.upiIds)} UPIs, "
            f"{len(intel.phishingLinks)} links, {len(intel.phoneNumbers)} phones"
        )
    
    # Step 3: Generate agent response using Gemini AI
    # Always use the AI agent for responses, regardless of scam detection
    reply, agent_note = await honeypot_agent.generate_response(
        current_message.text,
        session.conversation_history,
        session.scam_type or scam_type or "unknown",
        session_manager.get_message_count(session_id)
    )
    session_manager.add_agent_note(session_id, agent_note)
    
    # Add agent's response to conversation history
    agent_message = Message(
        sender="user",
        text=reply,
        timestamp=current_message.timestamp
    )
    session_manager.add_message(session_id, agent_message)
    

    
    return HoneypotResponse(
        status="success",
        reply=reply
    )


@app.get("/api/session/{session_id}")
async def get_session_info(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get session information (for debugging)."""
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
):
    """Get rate limit status for the API key."""
    remaining = rate_limiter.get_remaining(api_key)
    return {
        "limits": {
            "requests_per_minute": REQUESTS_PER_MINUTE,
            "requests_per_day": REQUESTS_PER_DAY
        },
        "remaining": remaining
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
